import logging
from typing import Any, Dict, List, Optional

from pydantic import validate_arguments

from src.models.api import ArticleStatistics
from src.models.api.job import Job
from src.models.api.statistics.article import ReferencesOverview
from src.models.api.statistics.article.content import (
    AggregateContentReferences,
    ContentReferences,
    CitationReferences,
    GeneralReferences,
)
from src.models.api.statistics.article.content.aggregate import (
    CiteQReferences,
    Cs1References,
)
from src.models.api.statistics.article.content.aggregate.cs1.cite_book_references import (
    CiteBookReferences,
)
from src.models.api.statistics.article.content.aggregate.cs1.cite_journal_references import (
    CiteJournalReferences,
)
from src.models.api.statistics.article.content.aggregate.cs1.cite_web_references import (
    CiteWebReferences,
)
from src.models.api.statistics.article.identifiers.unique_urls_aggregates import (
    UniqueUrlsAggregates,
)
from src.models.api.statistics.article.identifiers.urls import Urls
from src.models.api.statistics.article.identifiers.urls_aggregates import UrlsAggregates
from src.models.api.statistics.article.reference_types import ReferenceTypes
from src.models.api.statistics.reference import ReferenceStatistic, TemplateStatistics
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.article import WikipediaArticle
from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference
from src.wcd_base_model import WcdBaseModel

logger = logging.getLogger(__name__)


class WikipediaAnalyzer(WcdBaseModel):
    """This model contain all the logic for getting the
    article and reference statistics and mapping them to the API output model

    It does not handle storing on disk.
    """

    job: Job
    article: Optional[WikipediaArticle] = None
    article_statistics: Optional[ArticleStatistics] = None
    # wikibase: Wikibase = IASandboxWikibase()
    wikitext: str = ""
    check_urls: bool = False

    @property
    def wari_id(self) -> str:
        if not self.job:
            raise MissingInformationError()
        if not self.article:
            raise MissingInformationError()
        return (
            f"{self.job.lang.value}."
            f"{self.job.site.value}.org.{self.article.page_id}"
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

    @property
    def __agg__(self) -> Optional[AggregateContentReferences]:
        if self.article and self.article.extractor:
            # logger.debug(
            #     f"self.article.extractor.number_of_references_"
            #     f"with_a_deprecated_template:{self.article.extractor.number_of_references_with_a_deprecated_template}"
            # )
            ae = self.article.extractor
            return AggregateContentReferences(
                bare_url_t=ae.number_of_bare_url_references,
                citation_t=ae.number_of_citation_template_references,
                citeq_t=CiteQReferences(
                    all=ae.number_of_citeq_references,
                ),
                cs1_t=self.__cs1_t__,
                # has_hash=ae.number_of_hashed_content_references,
                has_template=ae.number_of_content_reference_with_at_least_one_template,
                isbn_t=ae.number_of_isbn_template_references,
                multiple_t=ae.number_of_multiple_template_references,
                supported_template_we_prefer=(
                    ae.number_of_content_references_with_a_supported_template_we_prefer
                ),
                url_t=ae.number_of_url_template_references,
                without_a_template=ae.number_of_content_reference_without_a_template,
                with_deprecated_template=ae.number_of_references_with_a_deprecated_template,
                has_archive_details_url=ae.number_of_content_references_with_ia_details_link(),
                has_google_books_url_or_template=(
                    ae.number_of_content_references_with_google_books_template_or_url()
                ),
                has_web_archive_org_url=ae.number_of_content_references_with_ia_details_link(),
                url_found=ae.number_of_content_references_with_url_found,
            )
        else:
            return None

    @property
    def __cs1_t__(self) -> Optional[Cs1References]:
        if self.article and self.article.extractor:
            ae = self.article.extractor
            return Cs1References(
                all=ae.number_of_cs1_references,
                web=CiteWebReferences(
                    all=ae.number_of_cite_web_references,
                    has_google_books_url=(
                        ae.number_of_cite_web_references_with_google_books_link_or_template
                    ),
                    has_ia_details_url=ae.number_of_cite_web_references_with_ia_details_link,
                    has_wm_url=ae.number_of_cite_web_references_with_wm_link,
                    has_url=ae.number_of_cite_web_references_with_a_url,
                ),
                journal=(
                    CiteJournalReferences(
                        all=ae.number_of_cite_journal_references,
                        has_wm_url=ae.number_of_cite_journal_references_with_wm_link,
                        # has_ia_details_url=(
                        #     ae.number_of_cite_journal_references_with_ia_details_link
                        # ),
                        has_url=ae.number_of_cite_journal_references_with_a_url,
                        has_doi=ae.number_of_cite_journal_references_with_doi,
                    )
                ),
                book=CiteBookReferences(
                    all=ae.number_of_cite_book_references,
                    has_wm_url=ae.number_of_cite_book_references_with_wm_link,
                    has_ia_details_url=ae.number_of_cite_book_references_with_ia_details_link,
                    has_url=ae.number_of_cite_book_references_with_a_url,
                    has_isbn=ae.number_of_cite_book_references_with_isbn,
                ),
                others=ae.number_of_other_cs1_references,
            )
        else:
            return None

    @property
    def __urls__(self) -> Urls:
        if (
            self.article
            and self.article.extractor
            and self.article.extractor.number_of_urls
        ):
            ae = self.article.extractor
            urls = Urls(
                agg=UrlsAggregates(
                    all=ae.number_of_urls,
                    unique=UniqueUrlsAggregates(
                        all=ae.number_of_checked_unique_reference_urls,
                    ),
                ),
                first_level_domain_counts=ae.reference_first_level_domain_counts,
                urls_found=True,
            )
        else:
            urls = Urls()
        return urls

    @property
    def __references_overview__(self) -> ReferencesOverview:
        if not self.article or not self.article.extractor:
            raise MissingInformationError(
                "self.article or self.article.extractor was None"
            )
        else:
            ae = self.article.extractor
            return ReferencesOverview(
                all=ae.number_of_references,
                types=ReferenceTypes(
                    content=ContentReferences(
                        all=ae.number_of_content_references,
                        citation=CitationReferences(
                            all=ae.number_of_citation_references
                        ),
                        general=GeneralReferences(
                            all=ae.number_of_general_references,
                        ),
                        agg=self.__agg__,
                    ),
                    named=ae.number_of_empty_named_references,
                ),
            )

    def __gather_article_statistics__(self) -> None:
        if (
            self.article
            and not self.article.is_redirect
            and self.article.found_in_wikipedia
        ):
            if not self.article.extractor:
                raise MissingInformationError("self.article.extractor was None")
            has_references = self.article.extractor.has_references
            self.article_statistics = ArticleStatistics(
                # todo update to v2
                wari_id=self.wari_id,
                has_references=has_references,
                page_id=self.article.page_id,
                title=self.article.title,
                urls=self.__urls__,
            )
            if has_references:
                self.article_statistics.references = self.__references_overview__

    def get_statistics(self) -> Dict[str, Any]:
        if not self.article:
            self.__analyze__()
        if not self.article_statistics:
            self.__gather_article_statistics__()
            self.__gather_reference_statistics__()
        return self.__get_statistics_dict__()

    def __get_statistics_dict__(self) -> Dict[str, Any]:
        if self.article_statistics:
            return self.article_statistics.dict()
        else:
            return {}

    def __analyze__(self):
        """Helper method"""
        logger.debug("__analyze__: running")
        if self.job:
            if not self.article:
                self.__populate_article__()
            if self.article:
                self.article.fetch_and_extract_and_parse()

    def __gather_reference_statistics__(self):
        logger.debug("__gather_reference_statistics__: running")
        if (
            self.article_statistics
            and self.article_statistics.references
            and self.article.extractor.number_of_references > 0
        ):
            self.article_statistics.references.details = []
            for reference in self.article.extractor.references:
                if not reference.raw_reference:
                    raise MissingInformationError("raw_reference was None")
                rr = reference.raw_reference
                reference_statistics = ReferenceStatistic(
                    plain_text_in_reference=rr.plain_text_in_reference,
                    citation_template_found=rr.citation_template_found,
                    cs1_template_found=rr.cs1_template_found,
                    citeq_template_found=rr.citeq_template_found,
                    isbn_template_found=rr.isbn_template_found,
                    url_template_found=rr.url_template_found,
                    bare_url_template_found=rr.bare_url_template_found,
                    multiple_templates_found=rr.multiple_templates_found,
                    is_named_reference=rr.is_named_reference,
                    is_citation_reference=rr.is_citation_reference,
                    is_general_reference=rr.is_general_reference,
                    has_archive_details_url=rr.archive_org_slash_details_in_reference,
                    has_google_books_url_or_template=rr.google_books_url_or_template_found,
                    has_web_archive_org_url=rr.web_archive_org_in_reference,
                    url_found=rr.url_found,
                    isbn=reference.isbn,
                    doi=reference.doi,
                    wikitext=rr.get_wikicode_as_string,
                    urls=rr.checked_urls,
                    flds=rr.first_level_domains,
                    multiple_cs1_templates_found=rr.multiple_cs1_templates_found,
                    number_of_bareurl_templates=rr.number_of_bareurl_templates,
                    number_of_citation_templates=rr.number_of_citation_templates,
                    number_of_citeq_templates=rr.number_of_citeq_templates,
                    number_of_isbn_templates=rr.number_of_isbn_templates,
                    number_of_cs1_templates=rr.number_of_cs1_templates,
                    number_of_templates=rr.number_of_templates,
                    number_of_templates_missing_first_parameter=rr.number_of_templates_missing_first_parameter,
                    is_valid_qid=reference.is_valid_qid,
                    wikidata_qid=reference.wikidata_qid,
                    number_of_url_templates=rr.number_of_url_templates,
                    number_of_webarchive_templates=rr.number_of_webarchive_templates,
                    templates=self.__gather_template_statistics__(reference=reference),
                    known_multiref_template_found=rr.known_multiref_template_found,
                )
                self.article_statistics.references.details.append(reference_statistics)
        if not self.article_statistics:
            logger.debug(
                "self.article_statistics was None "
                "so we skip gathering reference statistics"
            )

    def __populate_article__(self):
        logger.debug("__populate_article__: running")
        if self.job.title:
            # Todo consider propagating job further here
            self.article = WikipediaArticle(
                title=self.job.title,
                wikimedia_site=self.job.site,
                language_code=self.job.lang.value,
                wikitext=self.wikitext,
                check_urls=self.check_urls,
            )
        else:
            raise MissingInformationError("Got no title")

    @validate_arguments
    def __gather_template_statistics__(
        self, reference: WikipediaReference
    ) -> List[TemplateStatistics]:
        from src.models.api import app

        app.logger.debug("__gather_template_statistics__: running")
        if not reference.raw_reference:
            raise MissingInformationError("raw_reference missing")
        number_of_templates = reference.raw_reference.number_of_templates
        if not number_of_templates:
            app.logger.info(
                f"no templates found for {reference.raw_reference.wikicode}"
            )
            return []
        else:
            app.logger.info(
                f"found {number_of_templates} templates in {reference.raw_reference.wikicode}"
            )
            template_statistics_list: List[TemplateStatistics] = []
            for template in reference.raw_reference.templates:
                stat = TemplateStatistics(
                    # TODO extract more information that the patrons might want
                    #  to know from the templates, e.g. the different persons
                    doi=template.get_doi,
                    is_bareurl_template=template.is_bareurl_template,
                    is_citation_template=template.is_citation_template,
                    is_citeq_template=template.is_citeq_template,
                    is_cs1_template=template.is_cs1_template,
                    is_isbn_template=template.is_isbn_template,
                    is_known_multiref_template=template.is_known_multiref_template,
                    is_url_template=template.is_url_template,
                    is_webarchive_template=template.is_webarchive_template,
                    isbn=template.get_isbn,
                    wikitext=template.wikitext,
                )
                if template.doi:
                    app.logger.info("Adding DOI details")
                    stat.doi_details = template.doi.get_cleaned_doi_object()
                template_statistics_list.append(stat)
            app.logger.debug(
                f"returning {len(template_statistics_list)} template_statistics objects"
            )
            return template_statistics_list
