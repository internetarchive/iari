from unittest import TestCase

from src.models.wikimedia.enums import AnalyzerReturn
from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer
from test_data.test_content import easter_island_excerpt, test_full_article


class TestWikipediaAnalyzer(TestCase):
    def test_get_statistics_valid_article_easter_island(self):
        # Test using excerpt so we don't rely on information from Wikipedia that might change
        wa = WikipediaAnalyzer(title="Easter Island", wikitext=easter_island_excerpt, testing=True)
        assert wa.get_statistics() == ('{"number_of_cs1_references": 2, "number_of_citation_references": 0, '
                                       '"number_of_bare_url_references": 0, "number_of_citeq_references": 0, '
                                       '"number_of_isbn_template_references": 0, '
                                       '"number_of_multiple_template_references": 0, '
                                       '"number_of_named_references": 1, "number_of_content_references": 2, '
                                       '"number_of_hashed_content_references": 2, '
                                       '"percent_of_content_references_with_a_hash": 100}')

    def test_get_statistics_valid_article_test(self):
        wa = WikipediaAnalyzer(title="Test", wikitext=test_full_article)
        assert wa.get_statistics() == ('{"number_of_cs1_references": 0, "number_of_citation_references": 0, '
                                       '"number_of_bare_url_references": 0, "number_of_citeq_references": 0, '
                                       '"number_of_isbn_template_references": 0, '
                                       '"number_of_multiple_template_references": 0, '
                                       '"number_of_named_references": 0, "number_of_content_references": 0, '
                                       '"number_of_hashed_content_references": 0, '
                                       '"percent_of_content_references_with_a_hash": 0}')

    def test_get_statistics_redirect(self):
        wa = WikipediaAnalyzer(title="WWII")
        assert wa.get_statistics() == AnalyzerReturn.IS_REDIRECT

    def test_get_statistics_not_found(self):
        wa = WikipediaAnalyzer(title="Test2222")
        assert wa.get_statistics() == AnalyzerReturn.NOT_FOUND

    def test__gather_statistics__(self):
        pass

    def test__analyze__(self):
        pass