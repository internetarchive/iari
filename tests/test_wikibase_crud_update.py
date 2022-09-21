import logging
from unittest import TestCase

from wikibaseintegrator import WikibaseIntegrator  # type: ignore

import config
from src.models.wikibase.crud import WikibaseCrud
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.wikipedia.references.english_wikipedia import (
    EnglishWikipediaReference,
)
from src.models.wikimedia.wikipedia.wikipedia_article import WikipediaArticle

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWikibaseCrudUpdate(TestCase):
    # def test_compare_and_update_claims_offline(self):
    #     old_data = dict(
    #         # oclc="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     new_data = dict(
    #         oclc="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     old_reference = EnglishWikipediaReference(**old_data)
    #     old_reference.wikibase = IASandboxWikibase()
    #     old_reference.finish_parsing_and_generate_hash()
    #     new_reference = EnglishWikipediaReference(**new_data)
    #     new_reference.wikibase = IASandboxWikibase()
    #     new_reference.finish_parsing_and_generate_hash()
    #     wppage = WikipediaPage(wikibase=IASandboxWikibase())
    #     title = "Test"
    #     wppage.__get_wikipedia_article_from_title__(title=title)
    #     wppage.__generate_hash__()
    #     wcu = WikibaseCrudUpdate(wikibase=IASandboxWikibase())
    #     wcu.compare_and_update_claims(
    #         entity=old_reference,
    #         wikipedia_article=wppage,
    #         wikibase_item=wcu.__prepare_new_reference_item__(
    #             page_reference=new_reference, wikipedia_article=wppage
    #         ),
    #     )

    # We only do online tests now that verify that everything was written to Wikibase correctly
    # def test_compare_claims_on_references_offline(self):
    #     wikibase = IASandboxWikibase()
    #     old_data = dict(
    #         # oclc="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     new_data = dict(
    #         oclc="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     old_reference = EnglishWikipediaReference(**old_data)
    #     old_reference.wikibase = wikibase
    #     old_reference.finish_parsing_and_generate_hash()
    #     new_reference = EnglishWikipediaReference(**new_data)
    #     new_reference.wikibase = wikibase
    #     new_reference.finish_parsing_and_generate_hash()
    #     new_reference.return_ = WikibaseReturn(uploaded_now=False, item_qid="")
    #     wppage = WikipediaArticle(wikibase=wikibase)
    #     title = "Test"
    #     wppage.__get_wikipedia_article_from_title__(title=title)
    #     wppage.__generate_hash__()
    #     wcu = WikibaseCrudUpdate(wikibase=wikibase, testing=True, wikipedia_article=wppage)
    #     wcu.new_item = wcu.__prepare_new_reference_item__(
    #         page_reference=new_reference, wikipedia_article=wppage, testing=True
    #     )
    #     wcu.existing_wikibase_item = wcu.__prepare_new_reference_item__(
    #         page_reference=old_reference, wikipedia_article=wppage, testing=True
    #     )
    #     # We expect 1 claims to be added but 2 in the list
    #     # because the hash is different after adding oclc because it is used for hashing
    #     # over self.url.
    #     assert WriteRequired.YES == wcu.compare_and_update_claims(
    #         entity=new_reference,
    #     )
    #     # console.print(claims_to_be_added)
    #     # assert len(claims_to_be_added) == 1
    #     # assert (
    #     #     claims_to_be_added[0].mainsnak.property_number
    #     #     == wikibase.OCLC_CONTROL_NUMBER
    #     # )
    #     # assert claims_to_be_added[0].mainsnak.datavalue["value"] == "test"

    def test_that_wbi_can_remove_claims(self):
        """This tests that WBI correctly marks claims as removed"""
        wikibase = IASandboxWikibase()
        data = dict(
            # oclc="test",
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = wikibase
        reference.finish_parsing_and_generate_hash()
        wppage = WikipediaArticle(wikibase=wikibase)
        title = "Test"
        wppage.__get_wikipedia_article_from_title__(title=title)
        wppage.__generate_hash__()
        wc = WikibaseCrud(wikibase=wikibase)
        item = wc.__prepare_new_reference_item__(
            page_reference=reference, wikipedia_article=wppage
        )
        item.claims.remove(property=wikibase.HASH)
        # We get a keyerror because WBI knows the item is only in memory and not from
        # a Wikibase and can thus be removed directly
        with self.assertRaises(KeyError):
            item.claims.get(wikibase.HASH)

    # def test_write_required(self):
    #     wikibase = IASandboxWikibase()
    #     wcu = WikibaseCrudUpdate(wikibase=wikibase)
    #     # get the wikibase_item
    #     wcu.__setup_wikibase_integrator_configuration__()
    #     # We don't need to login to get an item
    #     wbi = WikibaseIntegrator()
    #     wcu.existing_wikibase_item = wbi.item.get(entity_id="Q148")
    #     # delete the hash
    #     wcu.existing_wikibase_item.claims.remove(property=wikibase.HASH)
    #     claims = wcu.existing_wikibase_item.claims.get(wikibase.HASH)
    #     assert len(claims) == 1
    #     assert claims[0].removed is True
    #     assert wcu.write_required is True
    #
    # def test_write_not_required(self):
    #     wikibase = IASandboxWikibase()
    #     wcu = WikibaseCrudUpdate(wikibase=wikibase)
    #     # get the wikibase_item
    #     wcu.__setup_wikibase_integrator_configuration__()
    #     # We don't need to login to get an item
    #     wbi = WikibaseIntegrator()
    #     wcu.existing_wikibase_item = wbi.item.get(entity_id="Q148")
    #     # delete the hash
    #     assert wcu.write_required is False

    def test_update_of_title(self):
        wikibase = IASandboxWikibase()
        # instantiate a page to test on
        wppage = WikipediaArticle(wikibase=wikibase)
        title = "Test"
        wppage.__get_wikipedia_article_from_title__(title=title)
        wppage.__generate_hash__()
        title_ref = "test title"
        data = dict(
            # oclc="test",
            title=title_ref,
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = wikibase
        reference.finish_parsing_and_generate_hash()
        reference.upload_reference_and_insert_in_the_cache_if_enabled()
        wbi = WikibaseIntegrator()
        item = wbi.item.get(reference.return_.item_qid)
        titles = item.claims.get(wikibase.TITLE)
        # console.print(titles)
        assert title_ref == titles[0].mainsnak.datavalue["value"]
        new_title = "new test title"
        data = dict(
            # oclc="test",
            title=new_title,
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = wikibase
        reference.finish_parsing_and_generate_hash()
        # here we get he return_ set
        reference.upload_reference_and_insert_in_the_cache_if_enabled()
        reference.__setup_wikibase_crud_update__(wikipedia_article=wppage)
        reference.wikibase_crud_update.compare_and_update_claims(entity=reference)
        wbi = WikibaseIntegrator()
        item = wbi.item.get(reference.return_.item_qid)
        titles = item.claims.get(wikibase.TITLE)
        # console.print(titles)
        assert new_title == titles[0].mainsnak.datavalue["value"]
