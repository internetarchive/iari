from unittest import TestCase

from src import WcdImportBot


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
    # def test_rinse_all_items_and_cache(self):
    #     bot = WcdImportBot()
    #     bot.rinse_all_items_and_cache()
