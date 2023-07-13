import logging
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models.api.job.article_job import ArticleJob
from src.models.api.statistic.article import ArticleStatistics
from src.models.api.statistic.reference import ReferenceStatistic
from src.models.base import WariBaseModel
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.article import WikipediaArticle

logger = logging.getLogger(__name__)


class WikipediaAnalyzer(WariBaseModel):
    """This model contain all the logic for getting the
    article and reference statistics and mapping them to the API output model

    It does not handle storing on disk.
    """

    job: Optional[ArticleJob] = None
    article: Optional[WikipediaArticle] = None
    article_statistics: Optional[ArticleStatistics] = None
    # wikibase: Wikibase = IASandboxWikibase()
    reference_statistics: Optional[List[Dict[str, Any]]] = None
    dehydrated_reference_statistics: Optional[List[Dict[str, Any]]] = None

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
            if not self.article.revision_id:
                raise MissingInformationError("self.article.revision_id was None")
            if not self.article.revision_isodate:
                raise MissingInformationError("self.article.revision_isodate was None")
            if not self.article.revision_timestamp:
                raise MissingInformationError(
                    "self.article.revision_timestamp was None"
                )
            ae = self.article.extractor
            if not self.job.page_id:
                self.job.get_ids_from_mediawiki_api()
            self.article_statistics = ArticleStatistics(
                wari_id=self.job.wari_id,
                lang=self.job.lang,
                reference_statistics={
                    "named": ae.number_of_empty_named_references,
                    "footnote": ae.number_of_footnote_references,
                    "content": ae.number_of_content_references,
                    "general": ae.number_of_general_references,
                },
                page_id=self.article.page_id,
                title=self.job.title,
                urls=ae.raw_urls,
                fld_counts=ae.first_level_domain_counts,
                served_from_cache=False,
                site=self.job.domain.value,
                isodate=datetime.utcnow().isoformat(),
                ores_score=self.article.ores_details,
                revision_isodate=self.article.revision_isodate.isoformat(),
                revision_timestamp=self.article.revision_timestamp,
                revision_id=self.article.revision_id,
            )

    def get_statistics(self) -> Dict[str, Any]:
        if not self.job:
            raise MissingInformationError()
        if not self.article:
            self.__analyze__()
        if not self.article_statistics:
            self.__gather_article_statistics__()
            self.__gather_reference_statistics__()
            if self.job.dehydrate:
                self.__extract_dehydrated_references__()
                self.__insert_dehydrated_references_into_the_article_statistics__()
            else:
                self.__insert_full_references_into_the_article_statistics__()
        return self.__get_statistics_dict__()

    def __get_statistics_dict__(self) -> Dict[str, Any]:
        if self.article_statistics:
            return self.article_statistics.dict()
        else:
            return {}

    def __analyze__(self):
        """Helper method"""
        from src import app

        app.logger.debug("__analyze__: running")
        if self.job:
            if not self.article:
                self.__populate_article__()
            if self.article:
                self.article.fetch_and_extract_and_parse()

    def __gather_reference_statistics__(self):
        from src import app

        self.reference_statistics = []
        app.logger.debug("__gather_reference_statistics__: running")
        if (
            self.article
            and self.article.extractor
            and self.article.extractor.references
        ):
            app.logger.debug(
                f"Gathering reference statistics for "
                f"{self.article.extractor.number_of_references} references"
            )
            for reference in self.article.extractor.references:
                if not reference:
                    raise MissingInformationError("raw_reference was None")
                subtype = (
                    reference.footnote_subtype.value
                    if reference.footnote_subtype
                    else ""
                )
                # if not rr.get_wikicode_as_string:
                #     raise MissingInformationError()
                data = ReferenceStatistic(
                    flds=reference.unique_first_level_domains
                    if reference.unique_first_level_domains
                    else [],
                    footnote_subtype=subtype,
                    id=reference.reference_id,
                    template_names=reference.template_names,
                    templates=reference.get_template_dicts,
                    titles=reference.titles,
                    type=reference.reference_type.value,
                    urls=reference.raw_urls,
                    wikitext=reference.get_wikicode_as_string,
                    section=reference.section,
                    url_objects=reference.get_reference_url_dicts,
                    name=reference.get_name,
                ).dict()
                self.reference_statistics.append(data)
        if not self.article_statistics:
            app.logger.debug(
                "self.article_statistics was None "
                "so we skip gathering reference statistics"
            )

    def __populate_article__(self):
        from src import app

        app.logger.debug("__populate_article__: running")
        if self.job and self.job.title:
            # Todo consider propagating job further here
            self.article = WikipediaArticle(
                job=self.job,
            )
        else:
            raise MissingInformationError("Got no title")

    def __extract_dehydrated_references__(self):
        # We use a local variable here to avoid this regression
        # https://github.com/internetarchive/wari/issues/700
        self.dehydrated_reference_statistics = deepcopy(self.reference_statistics)
        for data in self.dehydrated_reference_statistics:
            # We return most of the data including the wikitext to accommodate
            # see https://github.com/internetarchive/iari/issues/831
            del data["templates"]
            del data["url_objects"]

    def __insert_dehydrated_references_into_the_article_statistics__(self):
        if self.article_statistics:
            self.article_statistics.dehydrated_references = (
                self.dehydrated_reference_statistics
            )

    def __insert_full_references_into_the_article_statistics__(self):
        """We return the full reference to accommodate IARE, see https://github.com/internetarchive/iari/issues/886"""
        if self.article_statistics:
            self.article_statistics.references = self.reference_statistics
