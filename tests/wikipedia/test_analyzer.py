from unittest import TestCase

from src.models.api.article_statistics import ArticleStatistics
from src.models.api.reference_statistics import ReferenceStatistics
from src.models.wikimedia.enums import AnalyzerReturn
from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    test_full_article,
)


class TestWikipediaAnalyzer(TestCase):
    def test_get_statistics_valid_article_easter_island(self):
        # Test using excerpt so we don't rely on information from Wikipedia that might change
        wa = WikipediaAnalyzer(
            title="Easter Island", wikitext=easter_island_head_excerpt, testing=True
        )
        assert wa.get_statistics() == {
            "number_of_bare_url_references": 0,
            "number_of_citation_references": 2,
            "number_of_citation_template_references": 0,
            "number_of_citeq_references": 0,
            "number_of_content_reference_with_at_least_one_template": 2,
            "number_of_content_reference_with_no_templates": 0,
            "number_of_content_references": 2,
            "number_of_cs1_references": 2,
            "number_of_general_references": 2,
            "number_of_hashed_content_references": 2,
            "number_of_isbn_template_references": 0,
            "number_of_multiple_template_references": 0,
            "number_of_named_references": 1,
            "number_of_references_with_a_supported_template": 2,
            "number_of_url_template_references": 0,
            "percent_of_content_references_with_a_hash": 100,
            "references": [
                {
                    "bare_url_template_found": False,
                    "citation_template_found": False,
                    "citeq_template_found": False,
                    "cs1_template_found": True,
                    "is_citation_reference": True,
                    "is_general_reference": False,
                    "is_named_reference": False,
                    "isbn_template_found": False,
                    "multiple_templates_found": False,
                    "plain_text_in_reference": False,
                    "url_template_found": False,
                    "wikitext": '<ref name="INE">{{cite web | url= '
                    "http://www.ine.cl/canales/chile_estadistico/"
                    "censos_poblacion_vivienda/censo_pobl_vivi.php "
                    "| title= Censo de Población y Vivienda 2002 | "
                    "work= [[National Statistics Institute "
                    "(Chile)|National Statistics Institute]] | "
                    "access-date= 1 May 2010 | url-status=live | "
                    "archive-url= "
                    "https://web.archive.org/web/20100715195638/"
                    "http://www.ine.cl/canales/chile_estadistico/"
                    "censos_poblacion_vivienda/censo_pobl_vivi.php "
                    "| archive-date= 15 July 2010}}</ref>",
                },
                {
                    "bare_url_template_found": False,
                    "citation_template_found": False,
                    "citeq_template_found": False,
                    "cs1_template_found": True,
                    "is_citation_reference": True,
                    "is_general_reference": False,
                    "is_named_reference": False,
                    "isbn_template_found": False,
                    "multiple_templates_found": False,
                    "plain_text_in_reference": False,
                    "url_template_found": False,
                    "wikitext": "<ref>{{cite web |language= es |url= "
                    "https://resultados.censo2017.cl/Home/Download "
                    "|title= Censo 2017 |work= [[National Statistics "
                    "Institute (Chile)|National Statistics "
                    "Institute]] |access-date= 11 May 2018 "
                    "|archive-url= "
                    "https://web.archive.org/web/20180511145942/"
                    "https://resultados.censo2017.cl/Home/Download "
                    "|archive-date= 11 May 2018 |url-status=dead "
                    "}}</ref>",
                },
                {
                    "bare_url_template_found": False,
                    "citation_template_found": False,
                    "citeq_template_found": False,
                    "cs1_template_found": False,
                    "is_citation_reference": True,
                    "is_general_reference": False,
                    "is_named_reference": True,
                    "isbn_template_found": False,
                    "multiple_templates_found": False,
                    "plain_text_in_reference": False,
                    "url_template_found": False,
                    "wikitext": '<ref name="INE"/>',
                },
            ],
        }

    def test_get_statistics_valid_article_test(self):
        wa = WikipediaAnalyzer(title="Test", wikitext=test_full_article)
        assert wa.get_statistics() == ArticleStatistics().dict(exclude={"cache"})

    def test_get_statistics_redirect(self):
        wa = WikipediaAnalyzer(title="WWII")
        assert wa.get_statistics() == AnalyzerReturn.IS_REDIRECT

    def test_get_statistics_not_found(self):
        wa = WikipediaAnalyzer(title="Test2222")
        assert wa.get_statistics() == AnalyzerReturn.NOT_FOUND

    # def test__gather_statistics__(self):
    #     pass
    #
    # def test__analyze__(self):
    #     pass

    def test__gather_reference_statistics_test(self):
        wa = WikipediaAnalyzer(title="Test", wikitext=test_full_article)
        wa.__analyze__()
        wa.article_statistics = ArticleStatistics()
        wa.__gather_reference_statistics__()
        # Verify that it is empty
        assert wa.article_statistics == ArticleStatistics().dict()

    def test__gather_reference_statistics_easter_island(self):
        wa = WikipediaAnalyzer(
            title="Easter Island", wikitext=easter_island_head_excerpt, testing=True
        )
        wa.__analyze__()
        wa.article_statistics = ArticleStatistics()
        wa.__gather_reference_statistics__()
        # Verify that it is populated correctly
        assert wa.article_statistics == ArticleStatistics(
            number_of_bare_url_references=0,
            number_of_citation_references=0,
            number_of_citation_template_references=0,
            number_of_citeq_references=0,
            number_of_content_reference_with_at_least_one_template=0,
            number_of_content_reference_with_no_templates=0,
            number_of_content_references=0,
            number_of_cs1_references=0,
            number_of_general_references=0,
            number_of_hashed_content_references=0,
            number_of_isbn_template_references=0,
            number_of_multiple_template_references=0,
            number_of_named_references=0,
            number_of_references_with_a_supported_template=0,
            number_of_url_template_references=0,
            percent_of_content_references_with_a_hash=0,
            references=[
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
                    wikitext='<ref name="INE">{{cite web | url= http://www.ine.cl/canales/'
                    "chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php | "
                    "title= Censo de Población y Vivienda 2002 | work= [[National Statistics Institute "
                    "(Chile)|National Statistics Institute]] | access-date= 1 May 2010 | url-status=live "
                    "| archive-url= https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/"
                    "chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php | "
                    "archive-date= 15 July 2010}}</ref>",
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
                    wikitext="<ref>{{cite web |language= es |url= https://resultados.censo2017.cl/"
                    "Home/Download |title= Censo 2017 |work= [[National Statistics Institute "
                    "(Chile)|National Statistics Institute]] |access-date= 11 May 2018 |"
                    "archive-url= https://web.archive.org/web/20180511145942/https://"
                    "resultados.censo2017.cl/Home/Download |archive-date= 11 May 2018 |"
                    "url-status=dead }}</ref>",
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
        )
