from unittest import TestCase

from src import WcdImportBot


class TestWcdImportBot(TestCase):
    def test_get_pages_by_range(self):
        bot = WcdImportBot(wikibase_url="test",
                           mediawiki_api_url="test",
                           mediawiki_index_url="test",
                           sparql_endpoint_url="test")
        pages = bot.get_pages_by_range()
        if pages is None or len(pages) == 0:
            self.fail()
