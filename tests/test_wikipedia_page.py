import logging
from unittest import TestCase

import config
from src import WcdImportBot, WikipediaPage

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)

class TestWikipediaPage(TestCase):
    def test_start(self):
        bot = WcdImportBot(max_count=10,
                           wikibase_url="test",
                           mediawiki_api_url="test",
                           mediawiki_index_url="test",
                           sparql_endpoint_url="test")
        pages = bot.get_pages_by_range()
        for page in pages:
            page.extract_references()
            logger.info(len(page.references))
        # self.fail()
