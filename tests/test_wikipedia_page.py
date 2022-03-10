import logging
from unittest import TestCase

import pywikibot

import config
from src import WikipediaPage, WikimediaSite, console

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWikipediaPage(TestCase):
    def test_extract_references(self):
        site = pywikibot.Site(code="en", fam=WikimediaSite.WIKIPEDIA.value)
        page = WikipediaPage(title="Anarchism", pywikibot_site=site)
        page.extract_references()
        logger.info(len(page.references))
        for ref in page.references:
            if config.loglevel == logging.INFO or config.loglevel == logging.DEBUG:
                console.print(type(ref))
                console.print(ref.dict())
        # self.fail()


    def test___parse_templates__(self):
        pass