from unittest import TestCase

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
from src.models.api.reference_statistics import ReferenceStatistics
from src.models.wikimedia.enums import AnalyzerReturn
from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    test_full_article,
)


class TestWikipediaAnalyzer(TestCase):
    def test_fetch_slash_title_article(self):
        """This takes forever because of url checking"""
        wa = WikipediaAnalyzer(
            job=Job(title="GNU/Linux_naming_controversy", testing=True),
            check_urls=False,
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
        """This test takes forever (11s)"""
        # FIXME implement mock requests to reduce test time
        wa = WikipediaAnalyzer(
            job=Job(title="Easter Island", testing=True),
            wikitext=easter_island_head_excerpt,
        )
        wa.get_statistics()
        # Verify that it is populated correctly
        assert wa.article_statistics.has_references is True
        print(wa.article_statistics)
        from src.models.api.get_statistics.references.content.aggregate.cs1.cite_journal_references import (
            CiteJournalReferences,
        )

        # remove non-reproducible data, sometimes the 200 times out
        wa.article_statistics.references.links = Links()
        # wa.article_statistics.references.details
        wa.article_statistics.references.first_level_domain_counts = []
        assert (
            ArticleStatistics(
                has_references=True,
                references=References(
                    all=3,
                    details=[
                        ReferenceStatistics(
                            plain_text_in_reference=False,
                            citation_template_found=False,
                            cs1_template_found=True,
                            citeq_template_found=False,
                            isbn_template_found=False,
                            url_template_found=False,
                            bare_url_template_found=False,
                            multiple_templates_found=False,
                            is_named_reference=False,
                            wikitext=(
                                '<ref name="INE">{{cite web | url'
                                "= http://www.ine.cl/canales/chile_estadistico/"
                                "censos_poblacion_vivienda/censo_pobl_vivi.php | title= Censo de"
                                " Población y Vivienda 2002 | work= [["
                                "National Statistics Institute (Chile)|National Statistics Institute]] |"
                                " access-date= 1 May 2010 | url-status=live | archive-url= https"
                                "://web.archive.org/web/20100715195638/http://www.ine"
                                ".cl/canales/chile_estadistico/censos_poblacion_vivienda/"
                                "censo_pobl_vivi.php | archive-date= 15 July 2010}}</ref>"
                            ),
                            is_citation_reference=True,
                            is_general_reference=False,
                        ),
                        ReferenceStatistics(
                            plain_text_in_reference=False,
                            citation_template_found=False,
                            cs1_template_found=True,
                            citeq_template_found=False,
                            isbn_template_found=False,
                            url_template_found=False,
                            bare_url_template_found=False,
                            multiple_templates_found=False,
                            is_named_reference=False,
                            wikitext=(
                                "<ref>{{cite web |language= es |url= https://resultados.censo2017.cl"
                                "/Home/Download |title= Censo 2017 |work= [["
                                "National Statistics Institute (Chile)|National Statistics Institute]] "
                                "|access-date= 11 May 2018 |archive-url= https://web.archive."
                                "org/web/20180511145942/https://resultados.censo2017.cl"
                                "/Home/Download |archive-date= 11 May 2018 |url-status=dead }}</ref>"
                            ),
                            is_citation_reference=True,
                            is_general_reference=False,
                        ),
                        ReferenceStatistics(
                            plain_text_in_reference=False,
                            citation_template_found=False,
                            cs1_template_found=False,
                            citeq_template_found=False,
                            isbn_template_found=False,
                            url_template_found=False,
                            bare_url_template_found=False,
                            multiple_templates_found=False,
                            is_named_reference=True,
                            wikitext='<ref name="INE"/>',
                            is_citation_reference=True,
                            is_general_reference=False,
                        ),
                    ],
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
                                        no_link=2,
                                    ),
                                    journal=CiteJournalReferences(
                                        all=0, has_wm_link=2, no_link=2, has_doi=0
                                    ),
                                    book=CiteBookReferences(
                                        all=0,
                                        has_wm_link=2,
                                        has_ia_details_link=0,
                                        no_link=2,
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
            == wa.article_statistics
        )
