import logging
from unittest import TestCase

import pywikibot

import config
from src import WikipediaPage, WikimediaSite, console

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

    def test_fix_dash(self):
        site = pywikibot.Site(code="en", fam=WikimediaSite.WIKIPEDIA.value)
        page = WikipediaPage(
            pywikibot_site=site,
            language_code="en",
            wikimedia_site=WikimediaSite.WIKIPEDIA,
        )
        page.__get_wikipedia_page_from_title__(title="Easter Island")
        page.__extract_and_parse_references__()
        logger.info(f"{len(page.references)} references found")
        for ref in page.references:
            if config.loglevel == logging.INFO or config.loglevel == logging.DEBUG:
                # console.print(ref.template_name)
                if (
                    ref.url
                    == "http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php"
                ):
                    console.print(ref.url, ref.archive_url)
