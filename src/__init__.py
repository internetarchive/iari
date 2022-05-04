import argparse
import logging
from typing import List, Optional, Any

from pydantic import BaseModel, validate_arguments
from pywikibot import Page, Site

import config
from src.helpers import console
from src.models.exceptions import DebugExit
from src.models.cache import Cache
from src.models.wikicitations import WCDItem, WikiCitations
from src.models.wikimedia.enums import WikimediaSite
from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class WcdImportBot(BaseModel):
    """This class controls the import bot

    The language code is the one used by Wikimedia Foundation"""

    language_code: str = "en"
    max_count: int = 10
    total_number_of_hashed_references: Optional[int]
    pages: Optional[List[Any]]
    percent_references_hashed_in_total: Optional[int]
    title: Optional[str]
    total_number_of_references: Optional[int]
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    language_wcditem: WCDItem = WCDItem.ENGLISH_WIKIPEDIA

    # pseudo code
    # for each pageid in range(1,1000)
    # get wikipedia page
    # extract templates
    # iterate templates we support
    # create page_reference objects for each one
    # generate item in wcd

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

    def __setup_argparse_and_return_args__(self):
        # TODO add possibility to specify the wikipedia language version to work on
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="""
    WCD Import Bot imports references and pages from Wikipedia

    Example adding one page:
    '$ wcdimportbot.py --import-title "Easter Island"'

    Example deleting one page:
    '$ wcdimportbot.py --delete-page "Easter Island"'

    Example rinsing the Wikibase and the cache:
    '$ wcdimportbot.py --rinse'
        """,
        )
        parser.add_argument(
            "-d",
            "--delete-page",
            help=(
                "Delete a single page from WikiCitations and the cache by title "
                "(Defaults to English Wikipedia for now). "
                "Note: This does not delete the reference items associated "
                "with the page."
            ),
        )
        parser.add_argument(
            "-i",
            "--import-title",
            help=(
                "Title to import from a Wikipedia (Defaults to English Wikipedia for now)"
            ),
        )
        parser.add_argument(
            "--rinse",
            action="store_true",
            help="Rinse all page and reference items and delete the cache",
        )
        return parser.parse_args()

    @validate_arguments
    def delete_one_page(self, title: str) -> str:
        """Deletes one page from WikiCitations"""
        with console.status(f"Deleting {title}"):
            page = WikipediaPage(
                language_code=self.language_code,
                wikimedia_site=self.wikimedia_site,
                language_wcditem=self.language_wcditem,
            )
            page.__get_wikipedia_page_from_title__(title=title)
            page.__generate_hash__()
            # delete from WCD
            cache = Cache()
            cache.connect()
            item_id = cache.check_page_and_get_wikicitations_qid(wikipedia_page=page)
            if item_id is not None:
                wc = WikiCitations()
                item = wc.__delete_item__(item_id=item_id)
                # delete from cache
                if page.md5hash is not None:
                    cache.delete_key(key=page.md5hash)
                    console.print(
                        f"Deleted {title} from both WikiCitations and the cache"
                    )
                    return item_id
                else:
                    raise ValueError("md5hash was None")
            else:
                raise ValueError("got no item id from the cache")

    def extract_and_upload_all_pages_to_wikicitations(self):
        [page.extract_and_upload_to_wikicitations() for page in self.pages]

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
                        language_wcditem=self.language_wcditem,
                    )
                )

    @validate_arguments
    def get_page_by_title(self, title: str):
        self.pages = []
        page = WikipediaPage(
            language_code=self.language_code,
            wikimedia_site=self.wikimedia_site,
            language_wcditem=self.language_wcditem,
        )
        page.__get_wikipedia_page_from_title__(title=title)
        self.pages.append(page)

    def print_statistics(self):
        self.__calculate_statistics__()
        logger.info(
            f"A total of {self.total_number_of_references} references "
            f"has been processed and {self.total_number_of_hashed_references} "
            f"({self.percent_references_hashed_in_total}%) could be hashed on "
            f"a total of {len(self.pages)} pages."
        )

    def rinse_all_items_and_cache(self):
        """Delete all page and reference items and clear the SSDB cache"""
        wc = WikiCitations(
            language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
        )
        wc.delete_all_page_and_reference_items()
        cache = Cache()
        cache.connect()
        cache.flush_database()

    def run(self):
        """This method handles runnig the bot
        based on the given command line arguments."""
        args = self.__setup_argparse_and_return_args__()
        if args.rinse is True:
            self.rinse_all_items_and_cache()
        elif args.import_title is not None:
            logger.info(f"importing title {args.import_title}")
            self.get_page_by_title(title=args.import_title)
            self.extract_and_upload_all_pages_to_wikicitations()
        elif args.delete_page is not None:
            logger.info("deleting page")
            self.delete_one_page(title=args.delete_page)
        else:
            console.print("Got no arguments. Try 'python wcdimportbot.py -h' for help")
