import logging
from unittest import TestCase

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
        reference.parse_persons()
        reference.generate_hash()
        assert len(reference.persons_without_role) > 0
        item = wc.__prepare_new_reference_item__(
            page_reference=reference, wikipedia_page=wppage
        )
        console.print(item.get_json())
        assert (
            item.claims.get(property=WCDProperty.AUTHOR_NAME_STRING.value) is not None
        )
        # logger.info(f"url: {reference.wikicitations_url}")
        #
        # wppage = wc.prepare_and_upload_wikipedia_page_item(
        #     wikipedia_page=wppage,
        # )
        # logger.info(f"url: {wppage.wikicitations_url}")
