import logging
from time import sleep
from typing import List
from unittest import TestCase
from requests import HTTPError

from pydantic import ValidationError
from wikibaseintegrator.models import Claim  # type: ignore
from wikibaseintegrator.wbi_exceptions import MWApiError  # type: ignore

import config
from src import console, WCDItem, WcdImportBot
from src.models.wikicitations import WCDProperty, WikiCitations
from src.models.wikimedia.wikipedia.templates.english_wikipedia_page_reference import (
    EnglishWikipediaPageReference,
)
from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWikiCitations(TestCase):
    def test_prepare_new_reference_item(self):
        from src.models.wikicitations import WikiCitations

        wc = WikiCitations(
            language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
        )
        wppage = WikipediaPage(
            language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
        )
        wppage.__get_wikipedia_page_from_title__(title="Democracy")
        reference = EnglishWikipediaPageReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
            }
        )
        reference.finish_parsing_and_generate_hash()
        assert len(reference.persons_without_role) > 0
        item = wc.__prepare_new_reference_item__(
            page_reference=reference, wikipedia_page=wppage
        )
        console.print(item.get_json())
        assert (
            item.claims.get(property=WCDProperty.AUTHOR_NAME_STRING.value) is not None
        )

    def test_prepare_new_wikipedia_page_item_invalid_qid(self):
        from src.models.wikicitations import WikiCitations

        wc = WikiCitations(
            language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
        )
        wppage = WikipediaPage(
            language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
        )
        wppage.__get_wikipedia_page_from_title__(title="Democracy")
        reference = EnglishWikipediaPageReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
            }
        )
        reference.finish_parsing_and_generate_hash()
        reference.wikicitations_qid = "test"
        wppage.references = []
        wppage.references.append(reference)
        with self.assertRaises(ValueError):
            wc.max_number_of_item_citations = 0
            wc.__prepare_new_wikipedia_page_item__(
                wikipedia_page=wppage,
            )
        # console.print(item.get_json())

        # logger.info(f"url: {wppage.wikicitations_url}")

    def test_prepare_new_wikipedia_page_item_valid_qid(self):
        from src.models.wikicitations import WikiCitations

        wc = WikiCitations(
            language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
        )
        wppage = WikipediaPage(
            language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
        )
        title = "Democracy"
        wppage.__get_wikipedia_page_from_title__(title=title)
        reference = EnglishWikipediaPageReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
            }
        )
        reference.finish_parsing_and_generate_hash()
        reference.wikicitations_qid = "Q1"
        wppage.references = []
        wppage.references.append(reference)
        wppage.__generate_hash__()
        # with self.assertRaises(ValueError):
        item = wc.__prepare_new_wikipedia_page_item__(
            wikipedia_page=wppage,
        )
        # console.print(item.get_json())
        # assert item.labels.get("en") == title
        citations: List[Claim] = item.claims.get(WCDProperty.CITATIONS.value)
        # console.print(citations[0].mainsnak.datavalue["value"]["id"])
        assert citations[0].mainsnak.datavalue["value"]["id"] == "Q1"
        # logger.info(f"url: {wppage.wikicitations_url}")

    def test_prepare_and_upload_wikipedia_page_item_valid_qid(self):
        from src.models.wikicitations import WikiCitations

        wc = WikiCitations(
            language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
        )
        wppage = WikipediaPage(
            language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
        )
        title = "Democracy"
        wppage.__get_wikipedia_page_from_title__(title=title)
        wppage.__generate_hash__()
        reference = EnglishWikipediaPageReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
            }
        )
        reference.finish_parsing_and_generate_hash()
        test_qid = "Q4"
        reference.wikicitations_qid = test_qid
        wppage.references = []
        wppage.references.append(reference)
        # with self.assertRaises(ValueError):
        with self.assertRaises(MWApiError):
            wc.prepare_and_upload_wikipedia_page_item(
                wikipedia_page=wppage,
            )
        # console.print(wcdqid)

    # def test_P19_claims(self):
    #     site = pywikibot.Site(code="en", fam=WikimediaSite.WIKIPEDIA.value)
    #
    #     page = WikipediaPage(
    #         pywikibot_site=site,
    #         language_code="en",
    #         wikimedia_site=WikimediaSite.WIKIPEDIA,
    #         # max_number_of_item_citations_to_upload=1,
    #     )
    #     page.__get_wikipedia_page_from_title__(title="Culture change")
    #     page.extract_and_upload_to_wikicitations()

    # def test_delete_all_page_items(self):
    #     wc = WikiCitations(
    #         language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
    #     )
    #     wc.__delete_all_page_items__()
    #
    # def test_delete_all_reference_items(self):
    #     wc = WikiCitations(
    #         language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
    #     )
    #     wc.__delete_all_reference_items__()

    def test_entity_url(self):
        wc = WikiCitations()
        result = wc.entity_url(qid="Q1")
        assert result == "https://wikicitations.wiki.opencura.com/wiki/Item:Q1"

    def test_entity_url_missing_arguments(self):
        wc = WikiCitations()
        with self.assertRaises(ValidationError):
            wc.entity_url()

    def test_get_all_page_items(self):
        # first import a page to make sure there is at least one to be found
        bot = WcdImportBot()
        # this page has no references
        bot.get_page_by_title(title="Test")
        bot.extract_and_upload_all_pages_to_wikicitations()
        console.print(
            f"Waiting {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
        )
        sleep(config.sparql_sync_waiting_time_in_seconds)
        wc = WikiCitations()
        result = wc.__get_all_page_items__()
        console.print(result)
        # {'head': {'vars': ['item']}, 'results': {'bindings': []}}
        bindings = result["results"]["bindings"]
        assert len(bindings) > 0
        bot.rinse_all_items_and_cache()
        # exit()
        # items = wc.__get_all_page_items__()
        # if items is None or len(items) == 0:
        #     self.fail("Got no items")

    def test_get_all_reference_items(self):
        # first import a page with at least one reference
        # to make sure there is at least one to be found
        bot = WcdImportBot()
        # this page has no references
        bot.get_page_by_title(title="Muskö naval base")
        bot.extract_and_upload_all_pages_to_wikicitations()
        console.print(
            f"Waiting {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
        )
        sleep(config.sparql_sync_waiting_time_in_seconds)
        wc = WikiCitations()
        result = wc.__get_all_reference_items__()
        console.print(result)
        # {'head': {'vars': ['item']}, 'results': {'bindings': []}}
        bindings = result["results"]["bindings"]
        assert len(bindings) > 0
        bot.rinse_all_items_and_cache()
        # exit()
        # items = wc.__get_all_page_items__()
        # if items is None or len(items) == 0:
        #     self.fail("Got no items")

    def test_get_items_via_sparql(self):
        wc = WikiCitations()
        with self.assertRaises(HTTPError):
            wc.__get_items_via_sparql__(query="test")
