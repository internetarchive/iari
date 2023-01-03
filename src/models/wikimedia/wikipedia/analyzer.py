import logging
from typing import Optional

from src import IASandboxWikibase, Wikibase
from src.helpers.console import console
from src.models.api.article_statistics import ArticleStatistics
from src.models.api.reference_statistics import ReferenceStatistics
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.enums import AnalyzerReturn, WikimediaSite
from src.models.wikimedia.wikipedia.article import WikipediaArticle
from src.wcd_base_model import WcdBaseModel

logger = logging.getLogger(__name__)


class WikipediaAnalyzer(WcdBaseModel):
    title: str = ""
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    language_code: str = "en"
    article: Optional[WikipediaArticle] = None
    article_statistics: Optional[ArticleStatistics] = None
    wikibase: Wikibase = IASandboxWikibase()
    wikitext: str = ""
    testing: bool = False

    def __gather_article_statistics__(self):
        if not self.article:
            self.__analyze__()
        if (
            self.article
            and not self.article.is_redirect
            and self.article.found_in_wikipedia
        ):
            self.article_statistics = ArticleStatistics(
                number_of_cs1_references=self.article.extractor.number_of_cs1_references,
                number_of_citation_references=self.article.extractor.number_of_citation_references,
                number_of_bare_url_references=self.article.extractor.number_of_bare_url_references,
                number_of_citeq_references=self.article.extractor.number_of_citeq_references,
                number_of_isbn_template_references=self.article.extractor.number_of_isbn_template_references,
                number_of_multiple_template_references=self.article.extractor.number_of_multiple_template_references,
                number_of_named_references=self.article.extractor.number_of_named_references,
                number_of_content_references=self.article.extractor.number_of_content_references,
                number_of_hashed_content_references=self.article.extractor.number_of_hashed_content_references,
                percent_of_content_references_with_a_hash=self.article.extractor.percent_of_content_references_with_a_hash,
                number_of_references_with_a_supported_template=self.article.extractor.number_of_references_with_a_supported_template,
                number_of_content_reference_with_no_templates=self.article.extractor.number_of_content_reference_with_no_templates,
                number_of_content_reference_with_at_least_one_template=self.article.extractor.number_of_content_reference_with_at_least_one_template,
            )

    def get_statistics(self):
        if not self.article_statistics:
            self.__gather_article_statistics__()
            self.__gather_reference_statistics__()
        if self.article_statistics:
            excludes = {"cache"}
            dictionary = self.article_statistics.dict(exclude=excludes)
            console.print(dictionary)
            return dictionary
        else:
            if self.article.is_redirect:
                return AnalyzerReturn.IS_REDIRECT
            elif not self.article.found_in_wikipedia:
                return AnalyzerReturn.NOT_FOUND
            else:
                logger.error(
                    "self.article_statistics was None and the article was found and is not a redirect"
                )

    def __analyze__(self):
        if self.title:
            self.article = WikipediaArticle(
                title=self.title,
                wikimedia_site=self.wikimedia_site,
                language_code=self.language_code,
                wikibase=self.wikibase,
                wikitext=self.wikitext,
                testing=self.testing,
            )
            self.article.extract_and_parse_references()
        else:
            raise MissingInformationError("Got no title")

    def __gather_reference_statistics__(self):
        if self.article_statistics and self.article.extractor.number_of_references > 0:
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
                )
                self.article_statistics.references.append(reference_statistics)
        if not self.article_statistics:
            logger.debug(
                "self.article_statistics was None "
                "so we skip gathering reference statistics"
            )
