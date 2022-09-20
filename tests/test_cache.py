import logging
from unittest import TestCase

import config
from src.models.cache import Cache, CacheReturn
from src.models.wikimedia.wikipedia.templates.wikipedia_reference import WikipediaReference

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestCache(TestCase):
    def test_connect(self):
        database = Cache()
        database.connect(host="archive-wcd.aws.scatter.red")

    def test_check_website_and_get_wikibase_qid(self):
        cache = Cache()
        cache.connect()
        reference = WikipediaReference(template_name="test")
        reference.first_level_domain_of_url_hash = "123"
        assert isinstance(cache.check_website_and_get_wikibase_qid(reference=reference), CacheReturn)

    # def test_drop(self):
    #     database = Cache()
    #     database.connect()
    #     database.drop()
    #     # self.fail()

    # def test_add_reference(self):
    #     if config.use_cache:
    #         bot = WcdImportBot(
    #         )
    #         bot.get_and_extract_page_by_title(
    #             title="!Action Pact!",
    #         )
    #         [page.__parse_templates__() for page in bot.pages]
    #         bot.print_statistics()
    #         pages = [page for page in bot.pages]
    #         references: List[WikipediaReference] = []
    #         for page in pages:
    #             if len(page.references) > 0:
    #                 references.extend(page.references)
    #         hashed_references = [
    #             reference for reference in references if reference.md5hash
    #         ]
    #         if len(hashed_references) > 0:
    #             logger.info(f"found {len(hashed_references)} hashed references")
    #             reference = hashed_references[0]
    #             console.print(reference)
    #             cache = Cache()
    #             cache.connect()
    #             cache.add_reference(reference=reference, wcdqid="test")
    #             check = cache.check_reference_and_get_wikicitations_qid(
    #                 reference=reference
    #             )
    #             print(f"check:{check}")
    #             # assert check is not None
    #             assert check == "test"
    #         else:
    #             raise ValueError("No hashed references found")

    def test_get_cache_information(self):
        if config.use_cache:
            cache = Cache()
            cache.connect()
            cache.get_cache_information()
