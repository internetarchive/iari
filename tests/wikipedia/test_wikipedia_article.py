import logging
from unittest import TestCase

from wikibaseintegrator import WikibaseIntegrator  # type: ignore

import config
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.enums import WikimediaDomain
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    easter_island_tail_excerpt,
)

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWikipediaArticle(TestCase):
    # def test_fix_dash(self):
    #     # TODO improve this test and document it, it does not make sense
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     page = WikipediaArticle(
    #         wikibase=IASandboxWikibase(),
    #         language_code="en",
    #         wikimedia_site=WikimediaSite.WIKIPEDIA,
    #         title="Easter Island",
    #     )
    #     # This uses internet which is not optimal
    #     page.__get_wikipedia_article_from_title__()
    #     page.extract_and_parse_references()
    #     logger.info(f"{len(page.extractor.references)} references found")
    #     for ref in page.extractor.references:
    #         if config.loglevel == logging.INFO or config.loglevel == logging.DEBUG:
    #             # console.print(ref.template_name)
    #             if (
    #                 ref.url
    #                 == "http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php"
    #             ):
    #                 console.print(ref.url, ref.archive_url)

    def test_fetch_page_data_and_parse_the_wikitext(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            language_code="en",
            wikimedia_domain=WikimediaDomain.wikipedia,
            title="Test",
        )
        page.__fetch_page_data__()
        assert page.page_id == 11089416
        assert page.title == "Test"
        assert page.found_in_wikipedia is True

    def test_fetch_page_data_invalid_title(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            language_code="en",
            wikimedia_domain=WikimediaDomain.wikipedia,
            title="Test2222",
        )
        page.__fetch_page_data__()
        assert page.found_in_wikipedia is False

    def test_fetch_page_data_slashed_title(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            language_code="en",
            wikimedia_domain=WikimediaDomain.wikipedia,
            title="GNU/Linux_naming_controversy",
        )
        page.__fetch_page_data__()
        assert page.found_in_wikipedia is True

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

        wp = WikipediaArticle(
            title="Easter island",
            # wikibase=IASandboxWikibase()
        )
        wp.__fetch_page_data__()
        assert wp.is_redirect is True
        wp = WikipediaArticle(
            title="Easter Island",
            # wikibase=IASandboxWikibase()
        )
        wp.__fetch_page_data__()
        assert wp.is_redirect is False

    # def test_fetch_wikidata_qid_enwiki(self):
    #     """Test fetching from enwiki"""
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(
    #         title="Easter island",  # wikibase=IASandboxWikibase()
    #     )
    #     wp.__fetch_wikidata_qid__()
    #     assert wp.wikidata_qid == "Q14452"
    #
    # def test_fetch_wikidata_qid_dawiki(self):
    #     """Test fetching from dawiki"""
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(title="Påskeøen", language_code="da")
    #     wp.__fetch_wikidata_qid__()
    #     assert wp.wikidata_qid == "Q14452"

    # DISABLED because it fails. we deprecated the method since 2.1.0-alpha2
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

    # def test___extract_and_parse_references_citeq(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(title="Påskeøen", language_code="da")
    #     wp.wikitext = "<ref>{{citeq|1}}</ref>"
    #     wp.fetch_and_extract_and_parse()
    #     assert wp.extractor.number_of_references == 1
    # assert (
    #     wp.extractor.citeq_references[0].raw_reference.templates[0].raw_template
    #     == "{{citeq|1}}"
    # )
    # assert (
    #     wp.extractor.citeq_references[0].raw_reference.templates[0].name == "citeq"
    # )

    def test___extract_and_parse_references_easter_island_head_excerpt(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(title="Easter Island")
        wp.wikitext = easter_island_head_excerpt
        wp.fetch_and_extract_and_parse()
        assert wp.extractor.number_of_references == 3
        assert wp.extractor.number_of_empty_named_references == 1
        assert wp.extractor.number_of_content_references == 2
        assert wp.extractor.content_references[0].raw_reference.number_of_templates == 1
        assert wp.extractor.content_references[0].raw_reference.templates[
            0
        ].raw_template == (
            "{{cite web | url= http://www.ine.cl/canales/chile_estadistico/censos_poblacion_viviend"
            "a/censo_pobl_vivi.php | title= Censo de Población y Vivienda 2002 | work= [[National Statistics Institute "
            "(Chile)|National Statistics Institute]] | access-date= 1 May 2010 | url-stat"
            "us=live | archive-ur"
            "l= https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistic"
            "o/censos_poblacion_vivienda/censo_pobl_vivi.php | archive-date= 15 July 2010}}"
        )
        # print(wp.extractor.references[1].raw_reference.templates)
        assert wp.extractor.content_references[1].raw_reference.templates[
            0
        ].raw_template == (
            "{{cite web |language= es |url= https://resultados.censo2017.cl/Home/Download |title= Censo 2017 |wo"
            "rk= [[National Statistics Institute (Chile)|National Statistics Institute]] |access-d"
            "ate= 11 May 2018 |archive-url= https://web.archive.org/web/20180511145942/https://resultados.censo2"
            "017.cl/Home/Download |archive-date= 11 May 2018 |url-status=dead }}"
        )

    def test_easter_island(self):
        wikitext = f"{easter_island_head_excerpt}\n{easter_island_tail_excerpt}"
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(title="Easter Island")
        wp.wikitext = wikitext
        wp.fetch_and_extract_and_parse()
        assert wp.extractor.number_of_citation_references == 2
        assert wp.extractor.number_of_general_references == 32
        assert wp.extractor.number_of_content_references == 34

    # noinspection PyStatementEffect
    def test_quoted_title(self):
        from src import WikipediaArticle

        wp = WikipediaArticle(
            title="GNU/Linux_naming_controversy",
            # wikibase=IASandboxWikibase()
        )
        assert wp.quoted_title == "GNU%2FLinux_naming_controversy"
        wp = WikipediaArticle(
            title="",
            # wikibase=IASandboxWikibase()
        )
        with self.assertRaises(MissingInformationError):
            wp.quoted_title
