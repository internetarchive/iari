from unittest import TestCase

from src import WcdImportBot


class TestWcdImportBot(TestCase):
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

    def test_extract_references_from_20_pages(self):
        bot = WcdImportBot(
            max_count=100,
            wikibase_url="test",
            mediawiki_api_url="test",
            mediawiki_index_url="test",
            sparql_endpoint_url="test",
        )
        bot.get_pages_by_range()
        [page.extract_references() for page in bot.pages]
        bot.print_statistics()
