import logging
from typing import List, Optional

from pydantic import BaseModel
from pywikibot import Page, Site
from wikibaseintegrator.wbi_config import config as wbi_config

import config
from src.models.exceptions import DebugExit
from src.helpers import console
from src.models.wikimedia.enums import WikimediaSite
from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class WcdImportBot(BaseModel):
    language_code: str = "en"
    max_count: int = 10
    mediawiki_api_url: str
    mediawiki_index_url: str
    total_number_of_hashed_references: Optional[int]
    pages: Optional[List[WikipediaPage]]
    percent_references_hashed_in_total: Optional[int]
    sparql_endpoint_url: str
    total_number_of_references: Optional[int]
    wikibase_url: str
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA

    # pseudo code
    # for each pageid in range(1,1000)
    # get wikipedia page
    # extract templates
    # iterate templates we support
    # create reference objects for each one
    # generate item in wcd
    def __setup_wbi__(self):
        wbi_config["WIKIBASE_URL"] = self.wikibase_url
        wbi_config["MEDIAWIKI_API_URL"] = self.mediawiki_api_url
        wbi_config["MEDIAWIKI_INDEX_URL"] = self.mediawiki_index_url
        wbi_config["SPARQL_ENDPOINT_URL"] = self.sparql_endpoint_url

    def get_pages_by_range(self) -> None:
        self.pages = []
        count = 0
        # https://stackoverflow.com/questions/59605802/
        # use-pywikibot-to-download-complete-list-of-pages-from-a-mediawiki-server-without
        site = Site(code=self.language_code, fam=self.wikimedia_site.value)
        for page in site.allpages(namespace=0):
            if count == self.max_count:
                break
            page: Page = page
            if not page.isRedirectPage():
                count += 1
                # console.print(count)
                logger.info(f"{page.pageid} {page.title()} {page.isRedirectPage()}")
                # raise DebugExit()
                self.pages.append(
                    WikipediaPage(
                        pywikibot_page=page,
                        language_code=self.language_code,
                        wikimedia_site=self.wikimedia_site,
                    )
                )

    def __calculate_statistics__(self):
        """We want to have an overview while the bot is running
        about how many references could be imported"""
        self.total_number_of_hashed_references = sum(
            [page.number_of_hashed_references for page in self.pages]
        )
        self.total_number_of_references = sum(
            [page.number_of_references for page in self.pages]
        )
        if self.total_number_of_references == 0:
            self.percent_references_hashed_in_total = 0
        else:
            self.percent_references_hashed_in_total = int(
                self.total_number_of_hashed_references
                * 100
                / self.total_number_of_references
            )

    def print_statistics(self):
        self.__calculate_statistics__()
        logger.info(
            f"A total of {self.total_number_of_references} references "
            f"has been processed and {self.total_number_of_hashed_references} "
            f"({self.percent_references_hashed_in_total}%) could be hashed on "
            f"a total of {len(self.pages)} pages."
        )
