import logging
from datetime import datetime
from typing import Any, Dict, Optional

from src.models.api import ArticleStatistics
from src.models.api.job.article_job import ArticleJob
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.article import WikipediaArticle
from src.wcd_base_model import WcdBaseModel

logger = logging.getLogger(__name__)


class WikipediaAnalyzer(WcdBaseModel):
    """This model contain all the logic for getting the
    article and reference statistics and mapping them to the API output model

    It does not handle storing on disk.
    """

    job: ArticleJob
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

    def __gather_article_statistics__(self) -> None:
        if (
            self.article
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
                references=ae.reference_ids,
                page_id=self.article.page_id,
                title=self.article.title,
                urls=ae.raw_urls,
                fld_counts=ae.reference_first_level_domain_counts,
                served_from_cache=False,
                site=self.job.site.value,
                isodate=datetime.utcnow().isoformat(),
            )

    def get_statistics(self) -> Dict[str, Any]:
        if not self.article:
            self.__analyze__()
        if not self.article_statistics:
            self.__gather_article_statistics__()
            # self.__gather_reference_statistics__()
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

    # def __gather_reference_statistics__(self):
    #     logger.debug("__gather_reference_statistics__: running")
    #     if (
    #         self.article_statistics
    #         and self.article_statistics.references
    #         and self.article.extractor.number_of_references > 0
    #     ):
    #         self.article_statistics.references.details = []
    #         for reference in self.article.extractor.references:
    #             if not reference.raw_reference:
    #                 raise MissingInformationError("raw_reference was None")
    #             rr = reference.raw_reference
    #             reference_statistics = ReferenceStatistic(
    #                 plain_text_in_reference=rr.plain_text_in_reference,
    #                 citation_template_found=rr.citation_template_found,
    #                 cs1_template_found=rr.cs1_template_found,
    #                 citeq_template_found=rr.citeq_template_found,
    #                 isbn_template_found=rr.isbn_template_found,
    #                 url_template_found=rr.url_template_found,
    #                 bare_url_template_found=rr.bare_url_template_found,
    #                 multiple_templates_found=rr.multiple_templates_found,
    #                 is_named_reference=rr.is_named_reference,
    #                 is_citation_reference=rr.is_citation_reference,
    #                 is_general_reference=rr.is_general_reference,
    #                 has_archive_details_url=rr.archive_org_slash_details_in_reference,
    #                 has_google_books_url_or_template=rr.google_books_url_or_template_found,
    #                 has_web_archive_org_url=rr.web_archive_org_in_reference,
    #                 url_found=rr.url_found,
    #                 isbn=reference.isbn,
    #                 doi=reference.doi,
    #                 wikitext=rr.get_wikicode_as_string,
    #                 urls=rr.checked_urls,
    #                 flds=rr.first_level_domains,
    #                 multiple_cs1_templates_found=rr.multiple_cs1_templates_found,
    #                 number_of_bareurl_templates=rr.number_of_bareurl_templates,
    #                 number_of_citation_templates=rr.number_of_citation_templates,
    #                 number_of_citeq_templates=rr.number_of_citeq_templates,
    #                 number_of_isbn_templates=rr.number_of_isbn_templates,
    #                 number_of_cs1_templates=rr.number_of_cs1_templates,
    #                 number_of_templates=rr.number_of_templates,
    #                 number_of_templates_missing_first_parameter=rr.number_of_templates_missing_first_parameter,
    #                 is_valid_qid=reference.is_valid_qid,
    #                 wikidata_qid=reference.wikidata_qid,
    #                 number_of_url_templates=rr.number_of_url_templates,
    #                 number_of_webarchive_templates=rr.number_of_webarchive_templates,
    #                 templates=self.__gather_template_statistics__(reference=reference),
    #                 known_multiref_template_found=rr.known_multiref_template_found,
    #             )
    #             self.article_statistics.references.details.append(reference_statistics)
    #     if not self.article_statistics:
    #         logger.debug(
    #             "self.article_statistics was None "
    #             "so we skip gathering reference statistics"
    #         )

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

    # @validate_arguments
    # def __gather_template_statistics__(
    #     self, reference: WikipediaReference
    # ) -> List[TemplateStatistics]:
    #     from src.models.api import app
    #
    #     app.logger.debug("__gather_template_statistics__: running")
    #     if not reference.raw_reference:
    #         raise MissingInformationError("raw_reference missing")
    #     number_of_templates = reference.raw_reference.number_of_templates
    #     if not number_of_templates:
    #         app.logger.info(
    #             f"no templates found for {reference.raw_reference.wikicode}"
    #         )
    #         return []
    #     else:
    #         app.logger.info(
    #             f"found {number_of_templates} templates in {reference.raw_reference.wikicode}"
    #         )
    #         template_statistics_list: List[TemplateStatistics] = []
    #         for template in reference.raw_reference.templates:
    #             stat = TemplateStatistics(
    #                 # TODO extract more information that the patrons might want
    #                 #  to know from the templates, e.g. the different persons
    #                 doi=template.get_doi,
    #                 is_bareurl_template=template.is_bareurl_template,
    #                 is_citation_template=template.is_citation_template,
    #                 is_citeq_template=template.is_citeq_template,
    #                 is_cs1_template=template.is_cs1_template,
    #                 is_isbn_template=template.is_isbn_template,
    #                 is_known_multiref_template=template.is_known_multiref_template,
    #                 is_url_template=template.is_url_template,
    #                 is_webarchive_template=template.is_webarchive_template,
    #                 isbn=template.get_isbn,
    #                 wikitext=template.wikitext,
    #             )
    #             if template.doi:
    #                 app.logger.info("Adding DOI details")
    #                 stat.doi_details = template.doi.get_cleaned_doi_object()
    #             template_statistics_list.append(stat)
    #         app.logger.debug(
    #             f"returning {len(template_statistics_list)} template_statistics objects"
    #         )
    #         return template_statistics_list
