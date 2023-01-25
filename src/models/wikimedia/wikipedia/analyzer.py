import logging
from typing import Any, Dict, Optional

from src import IASandboxWikibase, Wikibase
from src.models.api.get_article_statistics.article_statistics import ArticleStatistics
from src.models.api.get_article_statistics.references import (
    Links,
    References,
    ReferenceTypes,
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
from src.models.api.get_article_statistics.references.links_aggregates import (
    LinksAggregates,
)
from src.models.api.get_article_statistics.references.reference_statistics import (
    ReferenceStatistics,
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
    testing: bool = False
    check_urls: bool = False

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
            return AggregateContentReferences(
                bare_url_t=self.article.extractor.number_of_bare_url_references,
                citation_t=self.article.extractor.number_of_citation_template_references,
                citeq_t=CiteQReferences(
                    all=self.article.extractor.number_of_citeq_references,
                ),
                cs1_t=self.__cs1_t__,
                has_hash=self.article.extractor.number_of_hashed_content_references,
                has_template=self.article.extractor.number_of_content_reference_with_at_least_one_template,
                isbn_t=self.article.extractor.number_of_isbn_template_references,
                multiple_t=self.article.extractor.number_of_multiple_template_references,
                supported_template_we_prefer=(
                    self.article.extractor.number_of_content_references_with_a_supported_template_we_prefer
                ),
                url_t=self.article.extractor.number_of_url_template_references,
                without_a_template=self.article.extractor.number_of_content_reference_without_a_template,
                with_deprecated_template=self.article.extractor.number_of_references_with_a_deprecated_template,
            )
        else:
            return None

    @property
    def __cs1_t__(self) -> Optional[Cs1References]:
        if self.article and self.article.extractor:
            return Cs1References(
                all=self.article.extractor.number_of_cs1_references,
                web=CiteWebReferences(
                    all=self.article.extractor.number_of_cite_web_references,
                    has_google_books_link=(
                        self.article.extractor.number_of_cite_web_references_with_google_books_link_or_template
                    ),
                    has_ia_details_link=self.article.extractor.number_of_cite_web_references_with_ia_details_link,
                    has_wm_link=self.article.extractor.number_of_cite_web_references_with_wm_link,
                    no_link=self.article.extractor.number_of_cite_web_references_with_no_link,
                ),
                journal=(
                    CiteJournalReferences(
                        all=self.article.extractor.number_of_cite_journal_references,
                        has_wm_link=(
                            self.article.extractor.number_of_cite_journal_references_with_wm_link
                        ),
                        has_ia_details_link=(
                            self.article.extractor.number_of_cite_journal_references_with_ia_details_link
                        ),
                        no_link=self.article.extractor.number_of_cite_journal_references_with_no_link,
                        has_doi=self.article.extractor.number_of_cite_journal_references_with_doi,
                    )
                ),
                book=CiteBookReferences(
                    all=self.article.extractor.number_of_cite_book_references,
                    has_wm_link=self.article.extractor.number_of_cite_book_references_with_wm_link,
                    has_ia_details_link=self.article.extractor.number_of_cite_book_references_with_ia_details_link,
                    no_link=self.article.extractor.number_of_cite_book_references_with_no_link,
                    has_isbn=self.article.extractor.number_of_cite_book_references_with_isbn,
                ),
                others=self.article.extractor.number_of_other_cs1_references,
            )
        else:
            return None

    @property
    def __links__(self) -> Links:
        if (
            self.article
            and self.article.extractor
            and self.article.extractor.number_of_checked_unique_reference_urls
        ):
            links = Links(
                agg=LinksAggregates(
                    all=self.article.extractor.number_of_checked_unique_reference_urls,
                    s200=self.article.extractor.number_of_reference_urls_with_code_200,
                    s3xx=self.article.extractor.number_of_reference_urls_with_code_3xx,
                    s404=self.article.extractor.number_of_reference_urls_with_code_404,
                    s5xx=self.article.extractor.number_of_reference_urls_with_code_5xx,
                    error=self.article.extractor.number_of_reference_urls_with_error,
                    no_dns=self.article.extractor.number_of_reference_urls_with_no_dns,
                    other_2xx=self.article.extractor.number_of_reference_urls_with_other_2xx,
                    other_4xx=self.article.extractor.number_of_reference_urls_with_other_4xx,
                ),
                links_found=True,
                malformed_url=self.article.extractor.number_of_reference_urls_with_malformed_url,
                details=self.article.extractor.reference_urls_dictionaries,
            )
        else:
            links = Links()
        return links

    @property
    def __references__(self) -> References:
        if not self.article or not self.article.extractor:
            raise MissingInformationError(
                "self.article or self.article.extractor was None"
            )
        else:
            return References(
                all=self.article.extractor.number_of_references,
                links=self.__links__,
                types=ReferenceTypes(
                    content=ContentReferences(
                        citation=CitationReferences(
                            all=self.article.extractor.number_of_citation_references
                        ),
                        general=GeneralReferences(
                            all=self.article.extractor.number_of_general_references,
                        ),
                        agg=self.__agg__,
                    ),
                    named=self.article.extractor.number_of_empty_named_references,
                ),
                first_level_domain_counts=self.article.extractor.reference_first_level_domain_counts,
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
                reference_statistics = ReferenceStatistics(
                    plain_text_in_reference=reference.raw_reference.plain_text_in_reference,
                    citation_template_found=reference.raw_reference.citation_template_found,
                    cs1_template_found=reference.raw_reference.cs1_template_found,
                    citeq_template_found=reference.raw_reference.citeq_template_found,
                    isbn_template_found=reference.raw_reference.isbn_template_found,
                    url_template_found=reference.raw_reference.url_template_found,
                    bare_url_template_found=reference.raw_reference.bare_url_template_found,
                    multiple_templates_found=reference.raw_reference.multiple_templates_found,
                    is_named_reference=reference.raw_reference.is_named_reference,
                    wikitext=reference.raw_reference.get_wikicode_as_string,
                    is_citation_reference=reference.raw_reference.is_citation_reference,
                    is_general_reference=reference.raw_reference.is_general_reference,
                    # links=reference.raw_reference.checked_urls,
                    # flds=reference.raw_reference.first_level_domains,
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
