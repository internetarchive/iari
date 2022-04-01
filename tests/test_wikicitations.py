import logging
from unittest import TestCase

import config
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
        qid = wc.prepare_and_upload_wikipedia_page_item(
            wikipedia_page=wppage,
        )
        if qid is not None:
            wppage.wikicitations_qid = qid
            wc.prepare_and_upload_reference_item(
                page_reference=EnglishWikipediaPageReference(
                    title="test", template_name="test", doi="test"
                ),
                wikipedia_page=wppage,
            )
            # self.fail()
        else:
            logger.error("qid was None")
