import logging
from unittest import TestCase

from wikibaseintegrator.wbi_exceptions import MissingEntityException  # type: ignore

import config
from src import WcdImportBot
from src.models.wikibase.enums import SupportedWikibase
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWcdImportBot(TestCase):
    """We decided to no longer delete pages so that functionality is now deprecated"""

    def test_rebuild_cache(self):
        bot = WcdImportBot(wikibase=IASandboxWikibase())
        bot.__rebuild_cache__()

    def test_flush_cache(self):
        bot = WcdImportBot(wikibase=IASandboxWikibase())
        bot.__flush_cache__()

    def test_import_one_page(self):
        bot = WcdImportBot(wikibase=IASandboxWikibase())
        bot.get_and_extract_page_by_title(title="Test")
        assert bot.processed_count == 1

    def test_get_pages_by_range(self):
        bot = WcdImportBot(
            target_wikibase=SupportedWikibase.IASandboxWikibase
        )
        bot.get_and_extract_pages_by_range(max_count=2)
        assert bot.processed_count == 2

    def test_get_pages_by_range_with_valid_category(self):
        bot = WcdImportBot(
            target_wikibase=SupportedWikibase.IASandboxWikibase
        )
        bot.get_and_extract_pages_by_range(max_count=2, category_title="World War II")
        assert bot.processed_count == 2

    def test_get_pages_by_range_with_invalid_category(self):
        bot = WcdImportBot(
            target_wikibase=SupportedWikibase.IASandboxWikibase
        )
        bot.get_and_extract_pages_by_range(max_count=2, category_title="World War II test test")
        assert bot.processed_count == 0


    def test___receive_workloads__(self):
        """We test that we can connect to rabbitmq and listen"""
        bot = WcdImportBot(wikibase=IASandboxWikibase(), testing=True)
        bot.__receive_workloads__()

    def test_wikibase_missing(self):
        WcdImportBot(testing=True)

    def test_target_wikibase_valid(self):
        WcdImportBot(
            target_wikibase=SupportedWikibase.IASandboxWikibase,
            testing=True,
        )

    # def test__gather_statistics__(self):
    #     """Todo make this test less slow"""
    #     bot = WcdImportBot(
    #         testing=True,
    #     )
    #     bot.__gather_statistics__()

    # DISABLED because we no longer delete pages
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

