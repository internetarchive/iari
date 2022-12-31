import logging
from unittest import TestCase

from wikibaseintegrator import WikibaseIntegrator  # type: ignore

import config
from src.helpers.console import console
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.enums import WikimediaSite
from test_data.test_content import easter_island_excerpt

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWikipediaArticle(TestCase):
    def test_fix_dash(self):
        # TODO improve this test and document it, it does not make sense
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            wikibase=IASandboxWikibase(),
            language_code="en",
            wikimedia_site=WikimediaSite.WIKIPEDIA,
            title="Easter Island",
        )
        # This uses internet which is not optimal
        page.__get_wikipedia_article_from_title__()
        page.extract_and_parse_references()
        logger.info(f"{len(page.extractor.references)} references found")
        for ref in page.extractor.references:
            if config.loglevel == logging.INFO or config.loglevel == logging.DEBUG:
                # console.print(ref.template_name)
                if (
                    ref.url
                    == "http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php"
                ):
                    console.print(ref.url, ref.archive_url)

    def test_fetch_page_data_and_parse_the_wikitext(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            wikibase=IASandboxWikibase(),
            language_code="en",
            wikimedia_site=WikimediaSite.WIKIPEDIA,
            title="Test",
        )
        page.__fetch_page_data__()
        assert page.page_id == 11089416
        assert page.title == "Test"
        assert page.found_in_wikipedia is True

    def test_fetch_page_data_invalid_title(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            wikibase=IASandboxWikibase(),
            language_code="en",
            wikimedia_site=WikimediaSite.WIKIPEDIA,
            title="Test2",
        )
        page.__fetch_page_data__()
        assert page.found_in_wikipedia is False

    # def test_get_wcdqid_from_hash_via_sparql(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     page = WikipediaArticle(
    #         wikibase=IASandboxWikibase(),
    #         language_code="en",
    #         wikimedia_site=WikimediaSite.WIKIPEDIA,
    #         title="Test",
    #     )
    #     # page.__fetch_page_data__(title="Test")
    #     page.extract_and_parse_and_upload_missing_items_to_wikibase()
    #     wcdqid = page.return_.item_qid
    #     console.print(
    #         f"Waiting {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
    #     )
    #     sleep(config.sparql_sync_waiting_time_in_seconds)
    #     check_wcdqid = page.__get_wcdqid_from_hash_via_sparql__(md5hash=page.md5hash)
    #     print(wcdqid, check_wcdqid)
    #     assert wcdqid == check_wcdqid

    def test_is_redirect(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(title="Easter island", wikibase=IASandboxWikibase())
        wp.__fetch_page_data__()
        assert wp.is_redirect is True
        wp = WikipediaArticle(title="Easter Island", wikibase=IASandboxWikibase())
        wp.__fetch_page_data__()
        assert wp.is_redirect is False

    def test_fetch_wikidata_qid_enwiki(self):
        """Test fetching from enwiki"""
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(title="Easter island", wikibase=IASandboxWikibase())
        wp.__fetch_wikidata_qid__()
        assert wp.wikidata_qid == "Q14452"

    def test_fetch_wikidata_qid_dawiki(self):
        """Test fetching from dawiki"""
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(
            title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
        )
        wp.__fetch_wikidata_qid__()
        assert wp.wikidata_qid == "Q14452"

    # DISABLED because it fails. we disabled the method since 2.1.0-alpha2
    # def test_get_title_from_wikidata(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(wdqid="Q1", wikibase=IASandboxWikibase())
    #     wp.__get_title_from_wikidata__()
    #     assert wp.title == "Universe"

    # def test___count_number_of_supported_templates_found_no_templates(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(
    #         title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
    #     )
    #     with self.assertRaises(MissingInformationError):
    #         wp.__count_number_of_supported_templates_found__()
    #
    # def test___count_number_of_supported_templates_found_with_template(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(
    #         title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
    #     )
    #     wp.wikitext = "{{citeq|1}}"
    #     wp.__extract_templates_from_the_wikitext__()
    #     assert len(wp.template_triples) == 1
    #
    # def test___extract_templates_from_the_wikitext_valid(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(
    #         title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
    #     )
    #     wp.wikitext = "{{citeq|1}}"
    #     wp.__extract_templates_from_the_wikitext__()
    #     assert len(wp.template_triples) == 1
    #
    # def test___extract_templates_from_the_wikitext_no_templates(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(
    #         title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
    #     )
    #     wp.wikitext = "{citeq|1}}testtestxxxx{}"
    #     wp.__extract_templates_from_the_wikitext__()
    #     assert len(wp.template_triples) == 0

    def test___extract_and_parse_references_citeq(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(
            title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
        )
        wp.wikitext = "<ref>{{citeq|1}}</ref>"
        wp.extract_and_parse_references()
        assert len(wp.extractor.references) == 1
        assert wp.extractor.references[0].raw_reference.templates[0].raw_template == "{{citeq|1}}"
        assert wp.extractor.references[0].first_template_name == "citeq"

    def test___extract_and_parse_references_easter_island_excerpt(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(title="Easter Island", wikibase=IASandboxWikibase())
        wp.wikitext = easter_island_excerpt
        wp.extract_and_parse_references()
        assert len(wp.extractor.references) == 3
        #print(wp.extractor.references)
        # print(wp.extractor.references[0].raw_reference.templates)
        assert wp.extractor.references[0].raw_reference.number_of_templates == 1
        assert wp.extractor.references[0].raw_reference.templates[0].raw_template == (
            "{{cite web | url= http://www.ine.cl/canales/chile_estadistico/censos_poblacion_viviend"
            "a/censo_pobl_vivi.php | title= Censo de Población y Vivienda 2002 | work= [[National Stati"
            "stics Institute (Chile)|National Statistics Institute]] | access-date= 1 May 2010 | url-stat"
            "us=live | archive-ur"
            "l= https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistic"
            "o/censos_poblacion_vivienda/censo_pobl_vivi.php | archive-date= 15 July 2010}}"
        )
        assert wp.extractor.references[0].first_template_name == "cite web"
        # print(wp.extractor.references[1].raw_reference.templates)
        assert wp.extractor.references[1].raw_reference.templates[0].raw_template == (
            "{{cite web |language= es |url= https://resultados.censo2017.cl/Home/Download |title= Censo 2017 |wo"
            "rk= [[National Statistics Institute (Chile)|National Statistics Institute]] |access-d"
            "ate= 11 May 2018 |archive-url= https://web.archive.org/web/20180511145942/https://resultados.censo2"
            "017.cl/Home/Download |archive-date= 11 May 2018 |url-status=dead }}"
        )
        assert wp.extractor.references[1].first_template_name == "cite web"
        print(wp.extractor.references[2].raw_reference)
        assert wp.extractor.references[2].raw_reference.templates[0].raw_template == (
            "{{cite web |last1=Dangerfield |first1=Whitney |title=The Mystery of Easter Island |url=https://www.sm"
            "ithsonianmag.com/travel/the-mystery-of-easter-island-151285298/ |website=[[Smiths"
            "onian (magazine)|Smithsonian Magazine]] |access-date=December 10, 2020 |date=March 31, 2007}}"
        )
        assert wp.extractor.references[2].first_template_name == "cite web"
        # assert wp.extractor.references[3].raw_reference.templates[0].raw_template == (
        #     "{{cite journal |author=Peiser, B. |url=http://www.uri.edu/artsci/ecn/starkey/ECN398%20-"
        #     "Ecology,%20Economy,%20Society/RAPANUI.pdf |archive-url=https://web.archive.org/web/2010061"
        #     "0062402/http://www.uri.edu/artsci/ecn/starkey/ECN398%20-Ecology,%20Economy,%20Society/RAPANU"
        #     "I.pdf |url-status=dead |archive-date=2010-06-10 |title=From Genocide to Ecocide: "
        #     "The Rape of Rapa Nui |doi=10.1260/0958305054672385 |journal=Energy & Environment |"
        #     "volume=16 |issue=3&4 |pages=513–539 |year=2005 |citeseerx=10.1.1.611.1103 |s2cid=155079232 }}"
        # )
        # assert wp.extractor.references[3].first_template_name == "cite journal"
        # assert wp.extractor.references[4].raw_reference.templates[0].raw_template == (
        #     "{{citation |url=http://www.leychile.cl/Navegar?idNorma=1026285 |title=List of C"
        #     "hilean Provinces |publisher=Congreso Nacional |access-date=20 February 2013 "
        #     "|url-status=live |archive-url=https://web.archive.org/web/20120910034328/http://www"
        #     ".leychile.cl/Navegar?idNorma=1026285 |archive-date=10 September 2012}}"
        # )
        # assert wp.extractor.references[4].first_template_name == "citation"
        # assert wp.extractor.references[5].raw_reference.templates[0].raw_template == (
        #     "{{cite web|url=https://redatam-ine.ine.cl/redbin/RpWebEngine.exe/Portal?BASE=CENSO_2"
        #     "017&lang=esp|title=Instituto Nacional de Estadísticas – REDATAM Procesamiento y disem"
        #     "inación|website=Redatam-ine.ine.cl|access-date=11 January 2019|archive-url=https://web.archi"
        #     "ve.org/web/20190527171611/https://redatam-ine.ine.cl/redbin/RpWebEngine.exe/Portal?B"
        #     "ASE=CENSO_2017&lang=esp|archive-date=27 May 2019|url-status=live}}"
        # )
        # assert wp.extractor.references[5].first_template_name == "cite web"
        # assert wp.extractor.references[6].raw_reference.templates[0].raw_template == (
        #     "{{citation|title=Welcome to Rapa Nui – Isla de Pascua – Easter Island|url=http://www.portal"
        #     "rapanui.cl/rapanui/informaciones.htm|work=Portal RapaNui, the island's official website|url-status=li"
        #     "ve|archive-url=https://web.archive.org/web/20120114041943/http://www.portalrapanui.cl/rapanui/in"
        #     "formaciones.htm|archive-date=14 January 2012}}"
        # )
        # assert wp.extractor.references[6].first_template_name == "citation"
        # assert wp.extractor.references[7].raw_reference.templates[0].raw_template == (
        #     "{{cite web |url=http://www.citypopulation.de/Pitcairn.html |title=Pitcairn Islands |author=Thomas B"
        #     "rinkhoff |date=1 February 2013 |website=Citypopulation.de |publisher=Thomas Brinkhoff |access-d"
        #     "ate=8 November 2013 |url-status=live |archive-url=https://web.archive.org/web/20131015182546/http://w"
        #     "ww.citypopulation.de/Pitcairn.html |archive-date=15 October 2013}}"
        # )
        # assert wp.extractor.references[7].first_template_name == "cite web"
        # assert wp.extractor.references[7].publisher == "Thomas Brinkhoff"
        # assert wp.extractor.references[7].title == "Pitcairn Islands"
        # assert wp.extractor.references[7].url == "http://www.citypopulation.de/Pitcairn.html"
