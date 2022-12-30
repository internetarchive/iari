import logging

from src import IASandboxWikibase, Wikibase
from src.helpers.console import console
from src.models.exceptions import MissingInformationError
from src.wcd_base_model import WcdBaseModel
from src.models.wikimedia.wikipedia.article import  WikipediaArticle
from src.models.wikimedia.enums import WikimediaSite
from src.models.wikimedia.wikipedia.article_statistics import ArticleStatistics

logger = logging.getLogger(__name__)


class WikipediaAnalyzer(WcdBaseModel):
    title: str = ""
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    language_code: str = "en"
    article: WikipediaArticle = None
    article_statistics: ArticleStatistics = None
    wikibase: Wikibase = IASandboxWikibase()

    def __gather_statistics__(self):
        if not self.article:
            self.__analyze__()
        if self.article:
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
                percent_of_content_references_with_a_hash=self.article.extractor.percent_of_content_references_with_a_hash
            )

    def print_statistics(self):
        if not self.article_statistics:
            self.__gather_statistics__()
        if self.article_statistics:
            excludes = {"cache"}
            console.print(self.article_statistics.dict(exclude=excludes))
        else:
            logger.error("self.article_statistics was None")

    def __analyze__(self):
        if self.title:
            self.article = WikipediaArticle(title=self.title, wikimedia_site=self.wikimedia_site,
                                            language_code=self.language_code, wikibase=self.wikibase)
            self.article.extract_and_parse_references()
        else:
            raise MissingInformationError("Got no title")