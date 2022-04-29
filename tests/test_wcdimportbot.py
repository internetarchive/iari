from time import sleep
from unittest import TestCase

from src import WcdImportBot, WikiCitations, console


class TestWcdImportBot(TestCase):
    pass
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
    def test_rinse_all_items_and_cache(self):
        bot = WcdImportBot()
        bot.rinse_all_items_and_cache()
        console.print("waiting 60 seconds for WDQS to sync after removal of all items")
        sleep(60)
        wc = WikiCitations()
        items = wc.__extract_item_ids__(sparql_result=wc.__get_all_page_items__())
        if items is not None and len(items) > 0:
            self.fail()
        items = wc.__extract_item_ids__(sparql_result=wc.__get_all_reference_items__())
        if items is not None and len(items) > 0:
            self.fail()
