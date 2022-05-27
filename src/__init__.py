import argparse
import logging
from typing import List, Optional, Any

from pydantic import BaseModel, validate_arguments

import config
from src.helpers import console
from src.models.cache import Cache
from src.models.exceptions import DebugExit
from src.models.ssdb_database import SsdbDatabase
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
            page.number_of_hashed_references for page in self.pages
        )
        self.total_number_of_references = sum(
            page.number_of_references for page in self.pages
        )
        if self.total_number_of_references == 0:
            self.percent_references_hashed_in_total = 0
        else:
            self.percent_references_hashed_in_total = int(
                self.total_number_of_hashed_references
                * 100
                / self.total_number_of_references
            )

    @staticmethod
    def __setup_argparse_and_return_args__():
        # TODO add possibility to specify the wikipedia language version to work on
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="""
    WCD Import Bot imports references and pages from Wikipedia

    Example adding one page:
    '$ ./wcdimportbot.py --import-title "Easter Island"'

    Example deleting one page:
    '$ ./wcdimportbot.py --delete-page "Easter Island"'

    Example looking up a hash:
    '$ ./wcdimportbot.py --lookup-hash e98adc5b05cb993cd0c884a28098096c'

    Example importing 5 pages (any page on the Wiki):
    '$ ./wcdimportbot.py --numerical-range 5'

    Example importing 5 pages from a specific category_title:
    '$ ./wcdimportbot.py --numerical-range 5 --category "World War II"'

    Example rinsing the Wikibase and the cache:
    '$ ./wcdimportbot.py --rinse'
        """,
        )
        parser.add_argument(
            "-c",
            "--category",
            help="Import range of pages from a specific category_title",
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
            "-r",
            "--numerical-range",
            help="Import range of pages",
        )
        parser.add_argument(
            "-i",
            "--import-title",
            help=(
                "Title to import from a Wikipedia (Defaults to English Wikipedia for now)"
            ),
        )
        parser.add_argument(
            "-l",
            "--lookup-hash",
            help=(
                "Lookup hash in the cache (if enabled) "
                "and WikiCitations via SPARQL (used mainly for debugging)"
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
            if config.use_cache:
                cache = Cache()
                cache.connect()
                item_id = cache.check_page_and_get_wikicitations_qid(
                    wikipedia_page=page
                )
            else:
                if page.md5hash is not None:
                    item_id = page.__get_wcdqid_from_hash_via_sparql__(
                        md5hash=page.md5hash
                    )
                else:
                    raise ValueError("page.md5hash was None")
            if item_id is not None and isinstance(item_id, str):
                wc = WikiCitations()
                wc.__delete_item__(item_id=item_id)
                # delete from cache
                if page.md5hash is not None:
                    if config.use_cache:
                        cache.delete_key(key=page.md5hash)
                        console.print(f"Deleted {title} from the cache")
                    console.print(f"Deleted {title} from WikiCitations")
                    return item_id
                else:
                    raise ValueError("md5hash was None")
            else:
                if config.use_cache:
                    raise ValueError("got no item id from the cache")
                else:
                    raise ValueError("got no item id from sparql")

    def extract_and_upload_all_pages_to_wikicitations(self):
        [page.extract_and_upload_to_wikicitations() for page in self.pages]

    @validate_arguments
    def get_pages_by_range(
        self, max_count: int = None, category_title: str = None
    ) -> None:
        """
        This method gets all pages in the main namespace up to max_count
        It uses pywikibot
        Caveat: the vanilla pywikibot is terribly verbose by default
        TODO: fork pywikibot and disable the verbose messages
        """
        from pywikibot import Category, Site  # type: ignore
        from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

        if max_count is not None:
            logger.debug(f"Setting max_count to {max_count}")
            self.max_count = int(max_count)
        self.pages = []
        count: int = 0
        # https://stackoverflow.com/questions/59605802/
        # use-pywikibot-to-download-complete-list-of-pages-from-a-mediawiki-server-without
        site = Site(code=self.language_code, fam=self.wikimedia_site.value)
        if category_title:
            category_page = Category(title=category_title, source=site)
            for page in site.categorymembers(category_page, member_type="page"):
                if count >= self.max_count:
                    logger.debug("breaking now")
                    break
                # page: Page = page
                #  and isinstance(page, Page)
                if not page.isRedirectPage():
                    count += 1
                    # console.print(count)
                    logger.info(
                        f"{page.pageid} {page.title()} Redirect:{page.isRedirectPage()}"
                    )
                    # raise DebugExit()
                    self.pages.append(
                        WikipediaPage(
                            language_code=self.language_code,
                            language_wcditem=self.language_wcditem,
                            latest_revision_date=page.editTime(),
                            latest_revision_id=page.latest_revision_id,
                            page_id=page.pageid,
                            title=str(page.title()),
                            wikimedia_site=self.wikimedia_site,
                            wikitext=page.text,
                        )
                    )
        else:
            for page in site.allpages(namespace=0):
                if count >= self.max_count:
                    break
                # page: Page = page
                if not page.isRedirectPage():
                    count += 1
                    # console.print(count)
                    logger.info(
                        f"{page.pageid} {page.title()} Redirect:{page.isRedirectPage()}"
                    )
                    # raise DebugExit()
                    self.pages.append(
                        WikipediaPage(
                            language_code=self.language_code,
                            language_wcditem=self.language_wcditem,
                            latest_revision_date=page.editTime(),
                            latest_revision_id=page.latest_revision_id,
                            page_id=page.pageid,
                            title=str(page.title()),
                            wikimedia_site=self.wikimedia_site,
                            wikitext=page.text,
                        )
                    )

    @validate_arguments
    def get_page_by_title(self, title: str):
        with console.status("Downloading page information"):
            self.pages = []
            page = WikipediaPage(
                language_code=self.language_code,
                wikimedia_site=self.wikimedia_site,
                language_wcditem=self.language_wcditem,
            )
            page.__get_wikipedia_page_from_title__(title=title)
            self.pages.append(page)

    @staticmethod
    @validate_arguments
    def lookup_hash(hash: str):
        """Lookup a hash and show the result to the user"""
        console.print(f"Lookup of hash {hash}")
        wc = WikiCitations(
            language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
        )
        if config.use_cache:
            ssdb = SsdbDatabase()
            cache_result = ssdb.get_value(key=hash)
            if cache_result:
                console.print(
                    f"CACHE: Found: {cache_result}, see {wc.entity_url(qid=str(cache_result))}",
                    style="green",
                )
            else:
                console.print("CACHE: Not found", style="red")
        sparql_result = wc.__get_wcdqids_from_hash__(md5hash=hash)
        if sparql_result:
            console.print(
                f"SPARQL: Found: {sparql_result}, see {wc.entity_url(qid=sparql_result[0])}",
                style="green",
            )
        else:
            console.print("SPARQL: Not found", style="red")

    def print_statistics(self):
        self.__calculate_statistics__()
        logger.info(
            f"A total of {self.total_number_of_references} references "
            f"has been processed and {self.total_number_of_hashed_references} "
            f"({self.percent_references_hashed_in_total}%) could be hashed on "
            f"a total of {len(self.pages)} pages."
        )

    @staticmethod
    def rinse_all_items_and_cache():
        """Delete all page and reference items and clear the SSDB cache"""
        wc = WikiCitations(
            language_code="en", language_wcditem=WCDItem.ENGLISH_WIKIPEDIA
        )
        wc.delete_imported_items()
        if config.use_cache:
            cache = Cache()
            cache.connect()
            cache.flush_database()

    def run(self):
        """This method handles running the bot
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
        elif args.numerical_range is not None:
            logger.info("Importing range of pages")
            max_count = args.numerical_range
            with console.status(f"Downloading {max_count} pages..."):
                self.get_pages_by_range(
                    max_count=max_count, category_title=args.category
                )
            self.extract_and_upload_all_pages_to_wikicitations()
        elif args.lookup_hash is not None:
            # We strip here to avoid errors caused by spaces
            self.lookup_hash(hash=args.lookup_hash.strip())
        else:
            console.print("Got no arguments. Try 'python wcdimportbot.py -h' for help")
