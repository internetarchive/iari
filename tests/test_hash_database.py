import logging
from typing import List
from unittest import TestCase

import config
from src import WcdImportBot, console
from src.models.hash_database import HashDatabase
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestHashDatabase(TestCase):
    # def test_initialize(self):
    #     database = HashDatabase()
    #     database.connect()
    #     database.initialize()
    #     # self.fail()
    #
    # def test_drop(self):
    #     database = HashDatabase()
    #     database.connect()
    #     database.drop()
    #     # self.fail()

    def test_add_reference(self):
        config.use_hash_database = True
        bot = WcdImportBot(
            table="testhashes",
            wikibase_url="test",
            mediawiki_api_url="test",
            mediawiki_index_url="test",
            sparql_endpoint_url="test",
        )
        bot.get_page_by_title(
            title="!Action Pact!",
        )
        [page.extract_references() for page in bot.pages]
        bot.print_statistics()
        pages = [page for page in bot.pages]
        references: List[WikipediaPageReference] = []
        for page in pages:
            if len(page.references) > 0:
                references.extend(page.references)
        hashed_references = [reference for reference in references if reference.md5hash]
        if len(hashed_references) > 0:
            reference = hashed_references[0]
            check = bot.database.check_reference_and_get_wikicitations_qid(
                reference=reference
            )
            print(f"check:{check}")
            console.print(bot.database.get_whole_table())
            assert check[1] != ""
            bot.database.drop_table_if_exists()
        else:
            raise ValueError("No hashed references found")
            # self.fail()
