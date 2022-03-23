import logging
from typing import List
from unittest import TestCase

import config
from src import WcdImportBot
from src.models.hash_database import HashDatabase
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestHashDatabase(TestCase):
    # def test_initialize(self):
    #     db = HashDatabase()
    #     db.connect()
    #     db.initialize()
    #     # self.fail()
    #
    # def test_drop(self):
    #     db = HashDatabase()
    #     db.connect()
    #     db.drop()
    #     # self.fail()

    def test_add_reference(self):
        db = HashDatabase()
        db.connect()
        db.drop_if_exists()
        db.initialize()
        bot = WcdImportBot(
            max_count=5,
            wikibase_url="test",
            mediawiki_api_url="test",
            mediawiki_index_url="test",
            sparql_endpoint_url="test",
        )
        bot.get_pages_by_range()
        [page.extract_references() for page in bot.pages]
        bot.print_statistics()
        pages = [page for page in bot.pages]
        references: List[WikipediaPageReference] = []
        for page in pages:
            if len(page.references) > 0:
                references.extend(page.references)
        hashed_references = [reference for reference in references if reference.md5hash]
        if len(hashed_references) > 0:
            logger.info("Adding the first reference we found")
            reference = hashed_references[0]
            reference.wikicitations_qid = "Q1"
            db.add_reference(reference=reference)
            check = db.check_reference_and_get_wikicitations_qid(reference=reference)
            print(f"check:{check}")
            assert check[1] == "Q1"
        # db.drop()
        else:
            raise ValueError("No hashed references found")
            # self.fail()
