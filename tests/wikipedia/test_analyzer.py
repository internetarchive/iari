from unittest import TestCase

from src.models.api.job.article_job import ArticleJob
from src.models.api.statistic.article import ArticleStatistics
from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    test_full_article,
)


class TestWikipediaAnalyzer(TestCase):
    def test_fetch_slash_title_article(self):
        job = ArticleJob(
            url="https://en.wikipedia.org/wiki/GNU/Linux_naming_controversy",
            testing=True,
        )
        job.__extract_url__()
        wa = WikipediaAnalyzer(job=job)
        wa.__populate_article__()
        # fixme This uses internet access
        wa.article.fetch_and_extract_and_parse()
        assert wa.article.found_in_wikipedia is True
        assert wa.found is True

    def test_get_statistics_valid_article_test(self):
        job = ArticleJob(
            url="https://en.wikipedia.org/wiki/Test",
            regex="bibliography|further reading|works cited|sources|external links",
        )
        job.__extract_url__()
        wa = WikipediaAnalyzer(job=job)
        data = wa.get_statistics()
        data["isodate"] = ""
        data["reference_statistics"] = {}
        assert (
            data
            == ArticleStatistics(
                page_id=11089416, title="Test", wari_id="en.wikipedia.org.11089416"
            ).dict()
        )

    def test_get_statistics_redirect(self):
        job = ArticleJob(url="https://en.wikipedia.org/wiki/WWII")
        job.__extract_url__()
        wa = WikipediaAnalyzer(job=job)
        wa.get_statistics()
        assert wa.is_redirect is True

    def test_get_statistics_not_found(self):
        job = ArticleJob(url="https://en.wikipedia.org/wiki/Test2222")
        job.__extract_url__()
        wa = WikipediaAnalyzer(job=job)
        wa.get_statistics()
        assert wa.found is False

    def test__gather_reference_statistics_test(self):
        job = ArticleJob(url="https://en.wikipedia.org/wiki/Test")
        job.__extract_url__()
        wa = WikipediaAnalyzer(job=job)
        wa.__analyze__()
        assert wa.article.wikitext != ""
        assert wa.is_redirect is False
        assert wa.found is True
        wa.__gather_reference_statistics__()
        assert len(wa.reference_statistics) == 35

    def test__gather_reference_statistics_sncaso(self):
        job = ArticleJob(url="https://en.wikipedia.org/wiki/SNCASO")
        job.__extract_url__()
        wa = WikipediaAnalyzer(job=job)
        wa.__analyze__()
        assert wa.article.wikitext != ""
        assert wa.is_redirect is False
        assert wa.found is True
        wa.get_statistics()
        assert len(wa.reference_statistics) == 63
        for reference in wa.reference_statistics:
            # this tests whether the deepcopy worked correctly
            assert "wikitext" in reference
            assert "templates" in reference

    # def test__get_statistics_easter_island(self):
    #     """This test takes forever (11s)"""
    #     # TODO update to v2
    #     # # FIXME implement mock requests to reduce test time
    #     self.fail()
