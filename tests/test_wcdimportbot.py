import logging
from unittest import TestCase

from pydantic import ValidationError
from wikibaseintegrator.wbi_exceptions import MissingEntityException  # type: ignore

import config
from src import WcdImportBot
from src.models.wikibase.enums import SupportedWikibase
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWcdImportBot(TestCase):
    # def test_delete_one_page(self):
    #     bot = WcdImportBot(wikibase=IASandboxWikibase())
    #     # bot.rinse_all_items_and_cache()
    #     bot.get_and_extract_page_by_title(title="Test")
    #     console.print(
    #         f"Waiting {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
    #     )
    #     sleep(config.sparql_sync_waiting_time_in_seconds)
    #     result = bot.delete_one_page(title="Test")
    #     assert result == Result.SUCCESSFUL

    def test_rebuild_cache(self):
        bot = WcdImportBot(wikibase=IASandboxWikibase())
        bot.__rebuild_cache__()

    def test_flush_cache(self):
        bot = WcdImportBot(wikibase=IASandboxWikibase())
        bot.__flush_cache__()

    # def test_import_one_page(self):
    #     bot = WcdImportBot(wikibase=IASandboxWikibase())
    #     bot.get_and_extract_page_by_title(title="Test")
    #     bot.

    # def test__gather_statistics__(self):
    #     bot = WcdImportBot(wikibase=IASandboxWikibase())
    #     bot.__gather_and_print_statistics__()
    #     # bot2 = WcdImportBot(wikibase=WikiCitationsWikibase())
    #     # bot2.__gather_statistics__()

    # def test_get_pages_by_range(self):
    #     bot = WcdImportBot(
    #         max_count=10,
    #         wikibase_url="test",
    #         mediawiki_api_url="test",
    #         mediawiki_index_url="test",
    #         sparql_endpoint_url="test",
    #     )
    #     pages = bot.get_pages_by_range()
    #     if pages is None or len(pages) != 10:
    #         self.fail()

    # def test_get_pages_by_range_200(self):
    #     bot = WcdImportBot(
    #         max_count=200,
    #         wikibase_url="test",
    #         mediawiki_api_url="test",
    #         mediawiki_index_url="test",
    #         sparql_endpoint_url="test",
    #     )
    #     pages = bot.get_pages_by_range()
    #     if pages is None or len(pages) != 200:
    #         self.fail()

    # def test_extract_references_from_20_pages(self):
    #     bot = WcdImportBot(
    #         max_count=20,
    #     )
    #     bot.get_pages_by_range()
    #     [page.extract_and_upload_to_wikicitations() for page in bot.pages]
    #     bot.print_statistics()

    # DISABLED because we don't want to rinse all items every time we run all tests
    # FIXME test against a test Wikibase instance so Mark can play with the production one himself
    # def test_rinse_all_items_and_cache(self):
    #     bot = WcdImportBot(wikibase=IASandboxWikibase())
    #     bot.rinse_all_items_and_cache()
    #     console.print(
    #         f"Waiting {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
    #     )
    #     sleep(config.sparql_sync_waiting_time_in_seconds)
    #     wc = WikiCitations()
    #     # How can we test this?
    #     items = wc.__extract_item_ids__(sparql_result=wc.__get_all_page_items__())
    #     items = wc.__extract_item_ids__(sparql_result=wc.__get_all_reference_items__())

    def test_receive(self):
        """We test that we can connect to rabbitmq and listen"""
        bot = WcdImportBot(wikibase=IASandboxWikibase(), testing=True)
        bot.__receive_workloads__()

    def test_target_wikibase_missing(self):
        with self.assertRaises(ValidationError):
            WcdImportBot(wikibase=IASandboxWikibase(), testing=True)

    def test_target_wikibase_valid(self):
        with self.assertRaises(ValidationError):
            WcdImportBot(
                wikibase=IASandboxWikibase(),
                testing=True,
                target_wikibase=SupportedWikibase.IASandboxWikibase,
            )
