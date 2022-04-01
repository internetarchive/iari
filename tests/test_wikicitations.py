from unittest import TestCase

from src.models.wikimedia.wikipedia.templates.english_wikipedia_page_reference import (
    EnglishWikipediaPageReference,
)
from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage


class TestWikiCitations(TestCase):
    def test_prepare_and_upload_reference_item(self):
        from src.models.wikicitations import WikiCitations

        wc = WikiCitations()
        wppage = WikipediaPage()
        wppage.__get_wikipedia_page_from_title__(title="Democracy")
        wc.prepare_and_upload_reference_item(
            page_reference=EnglishWikipediaPageReference(
                title="test", template_name="test", doi="test"
            ),
            wikipedia_page=wppage,
        )
        # self.fail()
