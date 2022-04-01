import logging
from unittest import TestCase

import config

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWikipediaPage(TestCase):
    # def test_extract_references(self):
    #     site = pywikibot.Site(code="en", fam=WikimediaSite.WIKIPEDIA.value)
    #     page = WikipediaPage(
    #         title="Anarchism",
    #         pywikibot_site=site,
    #         language_code="en",
    #         wikimedia_site=WikimediaSite.WIKIPEDIA,
    #     )
    #     page.__extract_references__()
    #     logger.info(len(page.references))
    #     for ref in page.references:
    #         if config.loglevel == logging.INFO or config.loglevel == logging.DEBUG:
    #             console.print(ref.template_name)
    #             # console.print(ref.dict())
    #     assert len(page.references) >= 134
    #     page = WikipediaPage(
    #         title="Democracy",
    #         pywikibot_site=site,
    #         language_code="en",
    #         wikimedia_site=WikimediaSite.WIKIPEDIA,
    #     )
    #     page.__extract_references__()
    #     logger.info(len(page.references))
    #     for ref in page.references:
    #         if config.loglevel == logging.INFO or config.loglevel == logging.DEBUG:
    #             console.print(ref.template_name)
    #     assert len(page.references) >= 216
    #     # self.fail()
    #
    # def test___parse_templates__(self):
    #     pass
    pass
