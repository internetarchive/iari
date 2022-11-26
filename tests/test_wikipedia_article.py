import logging
from unittest import TestCase

from wikibaseintegrator import WikibaseIntegrator  # type: ignore

import config
from src import console
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.enums import WikimediaSite

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWikipediaArticle(TestCase):
    def test_fix_dash(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            wikibase=IASandboxWikibase(),
            language_code="en",
            wikimedia_site=WikimediaSite.WIKIPEDIA,
            title="Easter Island",
        )
        page.__get_wikipedia_article_from_title__()
        page.__extract_and_parse_references__()
        logger.info(f"{len(page.references)} references found")
        for ref in page.references:
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

    def test_compare_data_and_update_additional_reference(self):
        """First delete the test page, then upload it with one reference.
        Then verify that the data in the Wikibase is correct"""
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        data = dict(
            title="Test book",
            url="https://archive.org/details/catalogueofshipw0000wils/",
            template_name="cite book",
        )
        from src.models.wikimedia.wikipedia.reference.english.english_reference import (
            EnglishWikipediaReference,
        )

        reference = EnglishWikipediaReference(**data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        string_data1 = dict(
            title="Test book with no identifier",
            template_name="cite book",
        )
        string_reference = EnglishWikipediaReference(**string_data1)
        string_reference.wikibase = IASandboxWikibase()
        string_reference.finish_parsing_and_generate_hash(testing=True)
        wp = WikipediaArticle(title="Test", wikibase=IASandboxWikibase())
        wp.references.extend([reference, string_reference])
        wp.extract_and_parse_and_upload_missing_items_to_wikibase()
        wbi = WikibaseIntegrator()
        item = wbi.item.get(wp.return_.item_qid)
        citations = item.claims.get(property=IASandboxWikibase().CITATIONS)
        string_citations = item.claims.get(
            property=IASandboxWikibase().STRING_CITATIONS
        )
        assert len(citations) == 1
        assert len(string_citations) == 1
        # press_enter_to_continue()
        wp2 = WikipediaArticle(title="Test", wikibase=IASandboxWikibase())
        string_data1 = dict(
            title="World War I",
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference2 = EnglishWikipediaReference(**string_data1)
        reference2.wikibase = IASandboxWikibase()
        reference2.finish_parsing_and_generate_hash()
        string_data2 = dict(
            title="Test another book with no identifier",
            template_name="cite book",
        )
        string_reference2 = EnglishWikipediaReference(**string_data2)
        string_reference2.wikibase = IASandboxWikibase()
        string_reference2.finish_parsing_and_generate_hash()
        wp2.references.extend(
            [reference, reference2, string_reference, string_reference2]
        )
        wp2.extract_and_parse_and_upload_missing_items_to_wikibase()
        item = wbi.item.get(wp2.return_.item_qid)
        citations = item.claims.get(property=IASandboxWikibase().CITATIONS)
        string_citations = item.claims.get(
            property=IASandboxWikibase().STRING_CITATIONS
        )
        assert len(citations) == 2
        assert len(string_citations) == 2

    def test_compare_data_and_update_removed_reference(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        data = dict(
            url="https://archive.org/details/catalogueofshipw0000wils/",
            template_name="cite book",
        )
        from src.models.wikimedia.wikipedia.reference.english.english_reference import (
            EnglishWikipediaReference,
        )

        reference = EnglishWikipediaReference(**data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        wp = WikipediaArticle(title="Test", wikibase=IASandboxWikibase())
        wp.references.append(reference)
        wp.extract_and_parse_and_upload_missing_items_to_wikibase()
        wbi = WikibaseIntegrator()
        item = wbi.item.get(wp.return_.item_qid)
        citations = item.claims.get(property=IASandboxWikibase().CITATIONS)
        assert len(citations) == 1
        wp = WikipediaArticle(title="Test", wikibase=IASandboxWikibase())
        wp.extract_and_parse_and_upload_missing_items_to_wikibase()
        item = wbi.item.get(wp.return_.item_qid)
        with self.assertRaises(KeyError):
            item.claims.get(property=IASandboxWikibase().CITATIONS)

    def test_is_redirect(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(title="Easter island", wikibase=IASandboxWikibase())
        wp.__fetch_page_data__()
        assert wp.is_redirect is True
        wp = WikipediaArticle(title="Easter Island", wikibase=IASandboxWikibase())
        wp.__fetch_page_data__()
        assert wp.is_redirect is False

    def test_fetch_wikidata_qid(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(title="Easter island", wikibase=IASandboxWikibase())
        wp.__fetch_wikidata_qid__()
        assert wp.wikidata_qid == "Q14452"

    # DISABLED because it fails. we disabled the method since 2.1.0-alpha2
    # def test_get_title_from_wikidata(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(wdqid="Q1", wikibase=IASandboxWikibase())
    #     wp.__get_title_from_wikidata__()
    #     assert wp.title == "Universe"
