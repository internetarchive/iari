import logging
from unittest import TestCase

from wikibaseintegrator.wbi_exceptions import MissingEntityException  # type: ignore

import config
from src import WcdImportBot
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

    # DEPRECATED since 2.1.0-alpha3
    # def test_flush_cache(self):
    #     bot = WcdImportBot(wikibase=IASandboxWikibase())
    #     bot.__flush_cache__()

    def test_import_one_page_and_make_sure_we_updated_ssdb(self):
        bot = WcdImportBot(wikibase=IASandboxWikibase(), page_title="Test")
        bot.get_and_extract_page_by_title()
        assert bot.wikipedia_article is not None
        from src.models.update_delay import UpdateDelay

        ud = UpdateDelay(object_=bot.wikipedia_article)
        assert ud.time_to_update(testing=True) is False
        assert ud.time_of_last_update is not None

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

    def test_get_pages_by_range(self):
        bot = WcdImportBot(wikibase=IASandboxWikibase())
        bot.__setup_cache__()
        bot.get_and_extract_pages_by_range(max_count=1)

    # def test_extract_references_from_20_pages(self):
    #     bot = WcdImportBot(
    #         max_count=20,
    #     )
    #     bot.get_pages_by_range()
    #     [page.extract_and_upload_to_wikicitations() for page in bot.pages]
    #     bot.print_statistics()

    # DISABLED because we don't want to rinse all items every time we run all tests
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

    def test_get_and_extract_page_by_title_invalid_page_title(self):
        bot = WcdImportBot(
            wikibase=IASandboxWikibase(), testing=True, page_title="asdfdsiowe"
        )
        bot.get_and_extract_page_by_title()
        assert bot.wikipedia_article.found_in_wikipedia is False
