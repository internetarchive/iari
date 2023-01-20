from unittest import TestCase

from src.helpers.console import console
from src.models.api.get_statistics.article_statistics import ArticleStatistics
from src.models.api.get_statistics.references import Links, References, ReferenceTypes
from src.models.api.get_statistics.references.content import (
    AggregateContentReferences,
    CitationReferences,
    ContentReferences,
    GeneralReferences,
)
from src.models.api.get_statistics.references.content.aggregate import (
    CiteQReferences,
    Cs1References,
)
from src.models.api.get_statistics.references.content.aggregate.cs1.cite_book_references import (
    CiteBookReferences,
)
from src.models.api.get_statistics.references.content.aggregate.cs1.cite_web_references import (
    CiteWebReferences,
)
from src.models.api.job import Job
from src.models.wikimedia.enums import AnalyzerReturn
from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    test_full_article,
)


class TestWikipediaAnalyzer(TestCase):
    def test_fetch_slash_title_article(self):
        wa = WikipediaAnalyzer(
            job=Job(title="GNU/Linux_naming_controversy", testing=True)
        )
        wa.__populate_article__()
        # fixme This uses internet access
        wa.article.fetch_and_extract_and_parse_and_generate_hash()
        assert wa.article.found_in_wikipedia is True

    def test_get_statistics_valid_article_test(self):
        wa = WikipediaAnalyzer(job=Job(title="Test"), wikitext=test_full_article)
        assert wa.get_statistics() == ArticleStatistics().dict(exclude={"cache"})

    def test_get_statistics_redirect(self):
        wa = WikipediaAnalyzer(job=Job(title="WWII"))
        assert wa.get_statistics() == AnalyzerReturn.IS_REDIRECT

    def test_get_statistics_not_found(self):
        wa = WikipediaAnalyzer(job=Job(title="Test2222"))
        assert wa.get_statistics() == AnalyzerReturn.NOT_FOUND

    def test__gather_reference_statistics_test(self):
        wa = WikipediaAnalyzer(job=Job(title="Test"), wikitext=test_full_article)
        wa.__analyze__()
        wa.article_statistics = ArticleStatistics()
        wa.__gather_reference_statistics__()
        # Verify that it is empty
        assert wa.article_statistics == ArticleStatistics().dict()

    def test__get_statistics_easter_island(self):
        wa = WikipediaAnalyzer(
            job=Job(title="Easter Island", testing=True),
            wikitext=easter_island_head_excerpt,
        )
        wa.get_statistics()
        # Verify that it is populated correctly
        assert wa.article_statistics.has_references is True
        console.print(wa.article_statistics)
        from src.models.api.get_statistics.references.content.aggregate.cs1.cite_journal_references import (
            CiteJournalReferences,
        )

        # remove non-reproducible data, sometimes the 200 times out
        wa.article_statistics.references.links = Links()
        wa.article_statistics.references.details = []
        # The counts are sorted so we keep the top one
        wa.article_statistics.references.first_level_domain_counts = []
        assert wa.article_statistics == ArticleStatistics(
            has_references=True,
            references=References(
                all=3,
                details=[],
                links=Links(all=0, s200=0, s404=0, s5xx=0, other=0, details=[]),
                types=ReferenceTypes(
                    content=ContentReferences(
                        citation=CitationReferences(all=2),
                        general=GeneralReferences(all=0),
                        agg=AggregateContentReferences(
                            bare_url_t=0,
                            cs1_t=Cs1References(
                                all=2,
                                web=CiteWebReferences(
                                    all=2,
                                    has_google_books_link=0,
                                    has_ia_details_link=0,
                                    has_wm_link=2,
                                    no_link=0,
                                ),
                                journal=CiteJournalReferences(
                                    all=0, has_wm_link=2, no_link=0, has_doi=0
                                ),
                                book=CiteBookReferences(
                                    all=0,
                                    has_wm_link=2,
                                    has_ia_details_link=0,
                                    no_link=0,
                                    has_isbn=0,
                                ),
                                others=0,
                            ),
                            has_hash=2,
                            citation_t=0,
                            citeq_t=CiteQReferences(all=0),
                            has_template=2,
                            isbn_t=0,
                            multiple_t=0,
                            supported_template_we_prefer=2,
                            url_t=0,
                            without_a_template=0,
                        ),
                    ),
                    named=1,
                ),
                first_level_domain_counts=[],
            ),
        )
