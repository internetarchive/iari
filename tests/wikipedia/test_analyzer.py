from unittest import TestCase

from src.models.api.get_article_statistics.article_statistics import ArticleStatistics
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
from src.models.api.get_article_statistics.references.urls_aggregates import (
    UrlsAggregates,
)
from src.models.api.job import Job
from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    test_full_article,
)


class TestWikipediaAnalyzer(TestCase):
    def test_fetch_slash_title_article(self):
        wa = WikipediaAnalyzer(
            job=Job(title="GNU/Linux_naming_controversy", testing=True),
            check_urls=False,
        )
        wa.__populate_article__()
        # fixme This uses internet access
        wa.article.fetch_and_extract_and_parse()
        assert wa.article.found_in_wikipedia is True
        assert wa.found is True

    def test_get_statistics_valid_article_test(self):
        wa = WikipediaAnalyzer(job=Job(title="Test"), wikitext=test_full_article)
        assert wa.get_statistics() == ArticleStatistics(title="Test").dict(
            exclude={"cache"}
        )

    def test_get_statistics_redirect(self):
        wa = WikipediaAnalyzer(job=Job(title="WWII"))
        wa.get_statistics()
        assert wa.is_redirect is True

    def test_get_statistics_not_found(self):
        wa = WikipediaAnalyzer(job=Job(title="Test2222"))
        wa.get_statistics()
        assert wa.found is False

    def test__gather_reference_statistics_test(self):
        wa = WikipediaAnalyzer(job=Job(title="Test"), wikitext=test_full_article)
        wa.__analyze__()
        wa.article_statistics = ArticleStatistics()
        wa.__gather_reference_statistics__()
        # Verify that it is empty
        assert wa.article_statistics == ArticleStatistics().dict()

    def test__get_statistics_easter_island(self):
        """This test takes forever (11s)"""
        # FIXME implement mock requests to reduce test time
        wa = WikipediaAnalyzer(
            job=Job(title="Easter Island", testing=True),
            wikitext=easter_island_head_excerpt,
            testing=True,
            check_urls=False,
        )
        wa.get_statistics()
        # Verify that it is populated correctly
        # print(wa.article_statistics)
        # remove non-reproducible data, sometimes the 200 times out
        # wa.article_statistics.references.urls = Urls()
        # wa.article_statistics.references.details
        # wa.article_statistics.references.first_level_domain_counts = []
        stat = wa.article_statistics
        assert stat.has_references is True
        assert stat.title == "Easter Island"
        assert stat.site == "wikipedia"
        assert stat.page_id == 0
        assert stat.timing == 0
        assert stat.timestamp == 0
        references = wa.article_statistics.references
        assert references.all == 3
        urls = references.urls
        assert urls.urls_found is True
        assert isinstance(urls.agg, UrlsAggregates)
        uagg = urls.agg
        assert uagg.all == 4
        uuagg = urls.agg.unique
        # We dont check urls during this
        # test for speed reasons so all these are 0
        assert uuagg.all == 0
        assert uuagg.error == 0
        assert uuagg.s5xx == 0
        assert uuagg.s404 == 0
        assert uuagg.s200 == 0
        assert uuagg.s3xx == 0
        assert uuagg.malformed_urls == 0
        assert uuagg.no_dns == 0
        assert uuagg.other_2xx == 0
        assert uuagg.other_4xx == 0
        types = references.types
        assert types.content is not None
        assert types.named == 1
        content = types.content
        assert content.all == 2
        agg = content.agg
        assert agg.url_found == 2
        assert agg.url_t == 0
        assert agg.bare_url_t == 0
        assert agg.citation_t == 0
        assert agg.citeq_t == CiteQReferences(all=0)
        assert agg.has_archive_details_url == 0
        # assert agg.has_hash == 2
        assert agg.has_template == 2
        assert agg.has_web_archive_org_url == 0
        assert agg.has_google_books_url_or_template == 0
        assert agg.cs1_t == Cs1References(
            all=2,
            web=CiteWebReferences(
                all=2,
                has_url=2,
                has_google_books_url=0,
                has_ia_details_url=0,
                has_wm_url=2,
            ),
            journal=CiteJournalReferences(all=0, has_wm_url=0, has_url=0, has_doi=0),
            book=CiteBookReferences(
                all=0, has_url=0, has_ia_details_url=0, has_isbn=0, has_wm_url=0
            ),
            others=0,
        )
        assert agg.isbn_t == 0
        assert agg.multiple_t == 0
        assert agg.supported_template_we_prefer == 2
        assert agg.with_deprecated_template == 0
        assert agg.without_a_template == 0
