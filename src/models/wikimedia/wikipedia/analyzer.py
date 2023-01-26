import logging
from typing import Any, Dict, Optional

from src import IASandboxWikibase, Wikibase
from src.models.api.get_article_statistics.article_statistics import ArticleStatistics
from src.models.api.get_article_statistics.references import (
    References,
    ReferenceTypes,
    Urls,
)
from src.models.api.get_article_statistics.references.content import (
    AggregateContentReferences,
    CitationReferences,
    ContentReferences,
    GeneralReferences,
)
from src.models.api.get_article_statistics.references.content.aggregate import (
    CiteQReferences,
    Cs1References,
)
from src.models.api.get_article_statistics.references.content.aggregate.cs1.cite_book_references import (
    CiteBookReferences,
)
from src.models.api.get_article_statistics.references.content.aggregate.cs1.cite_journal_references import (
    CiteJournalReferences,
)
from src.models.api.get_article_statistics.references.content.aggregate.cs1.cite_web_references import (
    CiteWebReferences,
)
from src.models.api.get_article_statistics.references.reference_statistics import (
    ReferenceStatistics,
)
from src.models.api.get_article_statistics.references.unique_urls_aggregates import (
    UniqueUrlsAggregates,
)
from src.models.api.get_article_statistics.references.urls_aggregates import (
    UrlsAggregates,
)
from src.models.api.job import Job
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.article import WikipediaArticle
from src.wcd_base_model import WcdBaseModel

logger = logging.getLogger(__name__)


class WikipediaAnalyzer(WcdBaseModel):
    """This model contain all the logic for getting the
    statistics and mapping them to the API output model"""

    job: Job
    article: Optional[WikipediaArticle] = None
    article_statistics: Optional[ArticleStatistics] = None
    wikibase: Wikibase = IASandboxWikibase()
    wikitext: str = ""
    check_urls: bool = False

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
                has_hash=ae.number_of_hashed_content_references,
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
                        s200=ae.number_of_unique_reference_urls_with_code_200,
                        s3xx=ae.number_of_unique_reference_urls_with_code_3xx,
                        s404=ae.number_of_unique_reference_urls_with_code_404,
                        s5xx=ae.number_of_unique_reference_urls_with_code_5xx,
                        error=ae.number_of_unique_reference_urls_with_error,
                        no_dns=ae.number_of_unique_reference_urls_with_no_dns,
                        other_2xx=ae.number_of_unique_reference_urls_with_other_2xx,
                        other_4xx=ae.number_of_unique_reference_urls_with_other_4xx,
                        malformed_urls=ae.number_of_unique_reference_urls_with_malformed_url,
                    ),
                ),
                urls_found=True,
                # details=ae.reference_urls_dictionaries,
            )
        else:
            urls = Urls()
        return urls

    @property
    def __references__(self) -> References:
        if not self.article or not self.article.extractor:
            raise MissingInformationError(
                "self.article or self.article.extractor was None"
            )
        else:
            ae = self.article.extractor
            return References(
                all=ae.number_of_references,
                urls=self.__urls__,
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
                first_level_domain_counts=ae.reference_first_level_domain_counts,
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
                has_references=has_references,
                page_id=self.article.page_id,
                title=self.article.title,
            )
            if has_references:
                self.article_statistics.references = self.__references__

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
                self.article.fetch_and_extract_and_parse_and_generate_hash()

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
                # DISABLED because it causes 502 sometimes
                # if not rr.check_urls_done:
                #     if not self.testing:
                #         raise MissingInformationError("check_urls_done was False")
                # if not rr.first_level_domains_done:
                #     raise MissingInformationError("first_level_domains_done was False")
                reference_statistics = ReferenceStatistics(
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
                language_code=self.job.lang,
                wikibase=self.wikibase,
                wikitext=self.wikitext,
                testing=self.testing,
                check_urls=self.check_urls,
            )
        else:
            raise MissingInformationError("Got no title")
