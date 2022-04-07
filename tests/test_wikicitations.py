import logging
from typing import List
from unittest import TestCase

from wikibaseintegrator.models import Claim

import config
from src import console
from src.models.wikicitations import WCDProperty
from src.models.wikimedia.wikipedia.templates.english_wikipedia_page_reference import (
    EnglishWikipediaPageReference,
)
from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWikiCitations(TestCase):
    def test_prepare_and_upload_reference_item(self):
        from src.models.wikicitations import WikiCitations

        wc = WikiCitations()
        wppage = WikipediaPage()
        wppage.__get_wikipedia_page_from_title__(title="Democracy")
        reference = EnglishWikipediaPageReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
            }
        )
        reference.finish_parsing_and_generate_hash()
        assert len(reference.persons_without_role) > 0
        item = wc.__prepare_new_reference_item__(
            page_reference=reference, wikipedia_page=wppage
        )
        console.print(item.get_json())
        assert (
            item.claims.get(property=WCDProperty.AUTHOR_NAME_STRING.value) is not None
        )

    def test_prepare_new_wikipedia_page_item_invalid_qid(self):
        from src.models.wikicitations import WikiCitations

        wc = WikiCitations()
        wppage = WikipediaPage()
        wppage.__get_wikipedia_page_from_title__(title="Democracy")
        reference = EnglishWikipediaPageReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
            }
        )
        reference.finish_parsing_and_generate_hash()
        reference.wikicitations_qid = "test"
        wppage.references = []
        wppage.references.append(reference)
        with self.assertRaises(ValueError):
            wc.max_number_of_item_citations = 0
            item = wc.__prepare_new_wikipedia_page_item__(
                wikipedia_page=wppage,
            )
        # console.print(item.get_json())

        # logger.info(f"url: {wppage.wikicitations_url}")

    def test_prepare_new_wikipedia_page_item_valid_qid(self):
        from src.models.wikicitations import WikiCitations

        wc = WikiCitations()
        wppage = WikipediaPage()
        title = "Democracy"
        wppage.__get_wikipedia_page_from_title__(title=title)
        reference = EnglishWikipediaPageReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
            }
        )
        reference.finish_parsing_and_generate_hash()
        reference.wikicitations_qid = "Q1"
        wppage.references = []
        wppage.references.append(reference)
        wppage.__generate_hash__()
        # with self.assertRaises(ValueError):
        wc.max_number_of_item_citations = 0
        item = wc.__prepare_new_wikipedia_page_item__(
            wikipedia_page=wppage,
        )
        # console.print(item.get_json())
        # assert item.labels.get("en") == title
        citations: List[Claim] = item.claims.get(WCDProperty.CITATIONS.value)
        # console.print(citations[0].mainsnak.datavalue["value"]["id"])
        assert citations[0].mainsnak.datavalue["value"]["id"] == "Q1"
        # logger.info(f"url: {wppage.wikicitations_url}")

    def test_prepare_and_upload_wikipedia_page_item_valid_qid(self):
        from src.models.wikicitations import WikiCitations

        wc = WikiCitations()
        wppage = WikipediaPage()
        title = "Democracy"
        wppage.__get_wikipedia_page_from_title__(title=title)
        wppage.__generate_hash__()
        reference = EnglishWikipediaPageReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
            }
        )
        reference.finish_parsing_and_generate_hash()
        test_qid = "Q4"
        reference.wikicitations_qid = test_qid
        wppage.references = []
        wppage.references.append(reference)
        # with self.assertRaises(ValueError):
        page_with_wcdqid = wc.prepare_and_upload_wikipedia_page_item(
            wikipedia_page=wppage,
        )
        console.print(page_with_wcdqid.wikicitations_qid)
