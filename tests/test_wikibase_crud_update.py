import logging
from datetime import datetime, timezone
from unittest import TestCase

from dateutil.parser import isoparse
from wikibaseintegrator import WikibaseIntegrator  # type: ignore

import config
from src import console
from src.models.wikibase.crud import WikibaseCrud
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.wikipedia.reference.english.english_reference import (
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
    #     wppage = WikipediaArticle(wikibase=IASandboxWikibase())
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

    def test_update_of_reference_statements(self):
        """We want to make sure that all fields except
        URL/ISBN/DOI can be updated on the reference"""
        wikibase = IASandboxWikibase()
        # instantiate a page to test on
        wppage = WikipediaArticle(wikibase=wikibase)
        title = "Test"
        wppage.__get_wikipedia_article_from_title__(title=title)
        wppage.__generate_hash__()
        title_ref = "test title"
        first1 = "Whitney"
        last1 = "Dangerfield"
        data = dict(
            # oclc="test",
            title=title_ref,
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
            first1=first1,
            last1=last1,
            access_date="December 10, 2020",
            date="March 31, 2007",
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = wikibase
        reference.finish_parsing_and_generate_hash()
        reference.upload_reference_and_insert_in_the_cache_if_enabled()
        # Update existing
        reference.__setup_wikibase_crud_update__(wikipedia_article=wppage)
        reference.wikibase_crud_update.compare_and_update_claims(entity=reference)
        console.print(f"See {reference.return_.item_qid}")
        wbi = WikibaseIntegrator()
        item = wbi.item.get(reference.return_.item_qid)
        titles = item.claims.get(wikibase.TITLE)
        assert title_ref == titles[0].mainsnak.datavalue["value"]
        full_name_strings = item.claims.get(wikibase.FULL_NAME_STRING)
        assert len(reference.persons_without_role) == 1
        first_author = reference.persons_without_role[0]
        assert (
            first_author.full_name == full_name_strings[0].mainsnak.datavalue["value"]
        )
        publication_dates = item.claims.get(wikibase.PUBLICATION_DATE)
        # see https://doc.wikimedia.org/Wikibase/master/php/md_docs_topics_json.html
        pd = isoparse(
            publication_dates[0].mainsnak.datavalue["value"]["time"].replace("+", "")
        )
        assert datetime(month=3, day=31, year=2007, tzinfo=timezone.utc) == pd
        access_dates = item.claims.get(wikibase.ACCESS_DATE)
        # see https://doc.wikimedia.org/Wikibase/master/php/md_docs_topics_json.html
        assert datetime(month=12, day=10, year=2020, tzinfo=timezone.utc) == isoparse(
            access_dates[0].mainsnak.datavalue["value"]["time"].replace("+", "")
        )
        new_title = "new test title"
        new_data = dict(
            # oclc="test",
            title=new_title,
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
            first1=f"{first1}-test",
            last1=f"{last1}-test",
            access_date="December 10, 2021",
            date="March 31, 2008",
        )
        reference = EnglishWikipediaReference(**new_data)
        reference.wikibase = wikibase
        reference.finish_parsing_and_generate_hash()
        # here we get he return_ set
        reference.upload_reference_and_insert_in_the_cache_if_enabled()
        reference.__setup_wikibase_crud_update__(wikipedia_article=wppage)
        reference.wikibase_crud_update.compare_and_update_claims(entity=reference)
        item = wbi.item.get(reference.return_.item_qid)
        new_titles = item.claims.get(wikibase.TITLE)
        assert new_title == new_titles[0].mainsnak.datavalue["value"]
        new_full_name_strings = item.claims.get(wikibase.FULL_NAME_STRING)
        assert len(reference.persons_without_role) == 1
        new_first_author = reference.persons_without_role[0]
        assert (
            new_first_author.full_name
            == new_full_name_strings[0].mainsnak.datavalue["value"]
        )
        wikibase_access_date = wikibase.parse_time_from_claim(
            item.claims.get(wikibase.ACCESS_DATE)[0]
        )
        assert reference.access_date == wikibase_access_date
        wikibase_publication_date = wikibase.parse_time_from_claim(
            item.claims.get(wikibase.PUBLICATION_DATE)[0]
        )
        assert reference.publication_date == wikibase_publication_date
        # TODO check that updating the dates also work
