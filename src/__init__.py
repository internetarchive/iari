import logging
from typing import List, Optional, Any

from pydantic import BaseModel, validate_arguments
from pywikibot import Page, Site

import config
from src.helpers import console
from src.models.exceptions import DebugExit
from src.models.cache import Cache
from src.models.wikimedia.enums import WikimediaSite
from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class WcdImportBot(BaseModel):
    language_code: str = "en"
    max_count: int = 10
    total_number_of_hashed_references: Optional[int]
    pages: Optional[List[Any]]
    percent_references_hashed_in_total: Optional[int]
    title: Optional[str]
    total_number_of_references: Optional[int]
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA

    # pseudo code
    # for each pageid in range(1,1000)
    # get wikipedia page
    # extract templates
    # iterate templates we support
    # create reference objects for each one
    # generate item in wcd

    def get_pages_by_range(self) -> None:
        def prepare_pywiki_site():
            return Site(code=self.language_code, fam=self.wikimedia_site.value)

        from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

        self.pages = []
        count = 0
        # https://stackoverflow.com/questions/59605802/
        # use-pywikibot-to-download-complete-list-of-pages-from-a-mediawiki-server-without
        site = prepare_pywiki_site()
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

    @validate_arguments
    def get_page_by_title(self, title: str):
        self.pages = []
        page = WikipediaPage(
            language_code=self.language_code,
            wikimedia_site=self.wikimedia_site,
        )
        page.__get_wikipedia_page_from_title__(title=title)
        self.pages.append(page)

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
