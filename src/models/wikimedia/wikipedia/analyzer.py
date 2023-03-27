import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models.api.job.article_job import ArticleJob
from src.models.api.statistic.article import ArticleStatistics
from src.models.api.statistic.reference import ReferenceStatistic
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.article import WikipediaArticle
from src.wcd_base_model import WcdBaseModel

logger = logging.getLogger(__name__)


class WikipediaAnalyzer(WcdBaseModel):
    """This model contain all the logic for getting the
    article and reference statistics and mapping them to the API output model

    It does not handle storing on disk.
    """

    job: Optional[ArticleJob] = None
    article: Optional[WikipediaArticle] = None
    article_statistics: Optional[ArticleStatistics] = None
    # wikibase: Wikibase = IASandboxWikibase()
    check_urls: bool = False
    reference_statistics: List[Dict[str, Any]] = []
    dehydrated_references: List[Dict[str, Any]] = []

    @property
    def wari_id(self) -> str:
        if not self.job:
            raise MissingInformationError()
        if not self.article:
            raise MissingInformationError()
        return (
            f"{self.job.lang.value}." f"{self.job.domain.value}.{self.article.page_id}"
        )

    @property
    def testing(self):
        if not self.job:
            raise MissingInformationError("no job")
        return self.job.testing

    @property
    def is_redirect(self) -> bool:
        if not self.article:
            raise MissingInformationError("self.article was None")
        return self.article.is_redirect

    @property
    def found(self) -> bool:
        if not self.article:
            raise MissingInformationError("self.article was None")
        return self.article.found_in_wikipedia

    def __gather_article_statistics__(self) -> None:
        if (
            self.job
            and self.article
            and not self.article.is_redirect
            and self.article.found_in_wikipedia
        ):
            if not self.article.extractor:
                raise MissingInformationError("self.article.extractor was None")
            ae = self.article.extractor
            self.article_statistics = ArticleStatistics(
                wari_id=self.wari_id,
                lang=self.job.lang.value,
                reference_statistics=dict(
                    named=ae.number_of_empty_named_references,
                    footnote=ae.number_of_citation_references,
                    content=ae.number_of_content_references,
                    general=ae.number_of_general_references,
                ),
                page_id=self.article.page_id,
                title=self.article.title,
                urls=ae.raw_urls,
                fld_counts=ae.reference_first_level_domain_counts,
                served_from_cache=False,
                site=self.job.domain.value,
                isodate=datetime.utcnow().isoformat(),
            )

    def get_statistics(self) -> Dict[str, Any]:
        if not self.job:
            raise MissingInformationError()
        if not self.article:
            self.__analyze__()
        if not self.article_statistics:
            self.__gather_article_statistics__()
            self.__gather_reference_statistics__()
            self.__extract_dehydrated_references__()
            self.__insert_dehydrated_references_into_the_article_statistics__()
        return self.__get_statistics_dict__()

    def __get_statistics_dict__(self) -> Dict[str, Any]:
        if self.article_statistics:
            return self.article_statistics.dict()
        else:
            return {}

    def __analyze__(self):
        """Helper method"""
        from src.models.api import app

        app.logger.debug("__analyze__: running")
        if self.job:
            if not self.article:
                self.__populate_article__()
            if self.article:
                self.article.fetch_and_extract_and_parse()

    def __gather_reference_statistics__(self):
        from src.models.api import app

        app.logger.debug("__gather_reference_statistics__: running")
        if (
            self.article
            and self.article.extractor
            and self.article.extractor.number_of_references > 0
        ):
            app.logger.debug(f"Gathering reference statistics for "
                             f"{self.article.extractor.number_of_references} references")
            for reference in self.article.extractor.references:
                if not reference.raw_reference:
                    raise MissingInformationError("raw_reference was None")
                rr = reference.raw_reference
                if rr.footnote_subtype:
                    subtype = rr.footnote_subtype.value
                else:
                    subtype = ""
                if not rr.get_wikicode_as_string:
                    raise MissingInformationError()
                self.reference_statistics.append(
                    ReferenceStatistic(
                        # identifiers=rr.identifiers,
                        flds=rr.first_level_domains,
                        footnote_subtype=subtype,
                        id=reference.reference_id,
                        template_names=rr.template_names,
                        templates=rr.get_template_dicts,
                        titles=rr.titles,
                        type=rr.reference_type.value,
                        urls=rr.raw_urls,
                        wikitext=rr.get_wikicode_as_string,
                    ).dict()
                )
        if not self.article_statistics:
            app.logger.debug(
                "self.article_statistics was None "
                "so we skip gathering reference statistics"
            )

    def __populate_article__(self):
        from src.models.api import app

        app.logger.debug("__populate_article__: running")
        if self.job and self.job.title:
            # Todo consider propagating job further here
            self.article = WikipediaArticle(
                title=self.job.title,
                wikimedia_domain=self.job.domain,
                language_code=self.job.lang.value,
                check_urls=self.check_urls,
            )
        else:
            raise MissingInformationError("Got no title")

    def __extract_dehydrated_references__(self):
        # We use a local variable here to avoid this regression
        # https://github.com/internetarchive/wari/issues/700
        statistics = self.reference_statistics
        for data in statistics:
            del data["templates"]
            del data["wikitext"]
            self.dehydrated_references.append(data)

    def __insert_dehydrated_references_into_the_article_statistics__(self):
        if self.article_statistics:
            self.article_statistics.dehydrated_references = self.dehydrated_references
