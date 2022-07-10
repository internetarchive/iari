import argparse
import logging
from typing import Optional

from pydantic import validate_arguments
from wikibaseintegrator import wbi_config  # type: ignore
from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore

from .helpers import console
from .models.cache import Cache
from .models.wikibase import Wikibase
from .models.wikibase.crud.delete import WikibaseCrudDelete
from .models.wikibase.crud.read import WikibaseCrudRead
from .models.wikibase.dictionaries import (
    wcd_externalid_properties,
    wcd_string_properties,
)
from .models.wikibase.sandbox_wikibase import SandboxWikibase
from .models.wikibase.wikicitations_wikibase import WikiCitationsWikibase
from .models.wikimedia.enums import WikimediaSite
from .wcd_base_model import WcdBaseModel

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class WcdImportBot(WcdBaseModel):
    """This class controls the import bot

    The language code is the one used by Wikimedia Foundation"""

    language_code: str = "en"
    max_count: int = 0  # 0 means disabled
    page_title: Optional[str]
    percent_references_hashed_in_total: Optional[int]
    # total_number_of_hashed_references: Optional[int]
    # total_number_of_references: Optional[int]
    wikibase: Wikibase = SandboxWikibase()
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA

    def __gather_and_print_statistics__(self):
        console.print(self.wikibase.title)
        wcr = WikibaseCrudRead(wikibase=self.wikibase)
        console.print(f"Number of pages: {wcr.number_of_pages}")
        console.print(f"Number of references: {wcr.number_of_references}")
        console.print(f"Number of websites: {wcr.number_of_website_items}")
        attributes = [a for a in dir(self.wikibase)]
        for attribute in attributes:
            if attribute in {**wcd_externalid_properties, **wcd_string_properties}:
                value = wcr.get_external_identifier_statistic(
                    property=getattr(self.wikibase, attribute)
                )
                console.print(f"Number of {attribute}: {value}")

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

    Example looking up a md5hash:
    '$ ./wcdimportbot.py --lookup-md5hash e98adc5b05cb993cd0c884a28098096c'

    Example importing 5 pages (any page on the Wiki):
    '$ ./wcdimportbot.py --max-range 5'

    Example importing 5 pages from a specific category title (recursively):
    '$ ./wcdimportbot.py --max-range 5 --category "World War II"'

    Example importing all pages from a specific category title (recursively):
    '$ ./wcdimportbot.py --category "World War II"'

    Example rinsing the Wikibase and the cache:
    '$ ./wcdimportbot.py --rinse'
        """,
        )
        parser.add_argument(
            "-c",
            "--category",
            help="Import range of pages from a specific category title recursively",
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
            "--max-range",
            help="Import max range of pages",
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
            "--lookup-md5hash",
            help=(
                "Lookup md5hash in the cache (if enabled) "
                "and WikiCitations via SPARQL (used mainly for debugging)"
            ),
        )
        parser.add_argument(
            "--rinse",
            action="store_true",
            help="Rinse all page and reference items and delete the cache",
        )
        parser.add_argument(
            "-s",
            "--statistics",
            action="store_true",
            help="Show statistics about the supported Wikibase instances",
        )
        parser.add_argument(
            "-wc",
            "--wikicitations",
            help="Work against Wikicitations. The bot defaults to sandboxwikibase.",
        )
        return parser.parse_args()

    def __setup_wikibase_integrator_configuration__(
        self,
    ) -> None:
        wbi_config.config["USER_AGENT"] = "wcdimportbot"
        wbi_config.config["WIKIBASE_URL"] = self.wikibase.wikibase_url
        wbi_config.config["MEDIAWIKI_API_URL"] = self.wikibase.mediawiki_api_url
        wbi_config.config["MEDIAWIKI_INDEX_URL"] = self.wikibase.mediawiki_index_url
        wbi_config.config["SPARQL_ENDPOINT_URL"] = self.wikibase.sparql_endpoint_url

    @validate_arguments
    def delete_one_page(self, title: str) -> str:
        """Deletes one page from WikiCitations"""
        with console.status(f"Deleting {title}"):
            from .models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

            page = WikipediaPage(
                wikibase=self.wikibase,
                language_code=self.language_code,
                wikimedia_site=self.wikimedia_site,
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
            if item_id:
                wc = WikibaseCrudDelete(wikibase=self.wikibase)
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
                    raise ValueError(
                        "Got no item id from sparql, "
                        "probably because WCDQS did not have time sync. "
                        "Try increasing the waiting time in config.py"
                    )

    @validate_arguments
    def get_and_extract_page_by_title(self, title: str):
        """Download and extract the page"""
        from .models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

        page = WikipediaPage(
            wikibase=self.wikibase,
            language_code=self.language_code,
            wikimedia_site=self.wikimedia_site,
        )
        page.__get_wikipedia_page_from_title__(title=title)
        page.extract_and_upload_to_wikicitations()

    @validate_arguments
    def get_and_extract_pages_by_range(
        self, max_count: int = None, category_title: str = None
    ) -> None:
        """
        This method gets all pages in the main namespace up to max_count
        It uses pywikibot
        """
        from pywikibot import Category, Site  # type: ignore

        from .models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

        if max_count is not None:
            logger.debug(f"Setting max_count to {max_count}")
            self.max_count = int(max_count)
        count: int = 0
        # https://stackoverflow.com/questions/59605802/
        # use-pywikibot-to-download-complete-list-of-pages-from-a-mediawiki-server-without
        site = Site(code=self.language_code, fam=self.wikimedia_site.value)
        if category_title:
            category_page = Category(title=category_title, source=site)
            for page in category_page.articles(recurse=True):
                if self.max_count and count >= self.max_count:
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
                    wikipedia_page = WikipediaPage(
                        wikibase=self.wikibase,
                        language_code=self.language_code,
                        latest_revision_date=page.editTime(),
                        latest_revision_id=page.latest_revision_id,
                        page_id=page.pageid,
                        title=str(page.title()),
                        wikimedia_site=self.wikimedia_site,
                        wikitext=page.text,
                    )
                    wikipedia_page.extract_and_upload_to_wikicitations()
        else:
            for page in site.allpages(namespace=0):
                if count >= self.max_count:
                    break
                # page: Page = page
                if not page.isRedirectPage():
                    count += 1
                    # console.print(count)
                    logger.info(f"{page.pageid} {page.page_title()}")
                    # raise DebugExit()
                    wikipedia_page = WikipediaPage(
                        language_code=self.language_code,
                        latest_revision_date=page.editTime(),
                        latest_revision_id=page.latest_revision_id,
                        page_id=page.pageid,
                        title=str(page.page_title()),
                        wikimedia_site=self.wikimedia_site,
                        wikitext=page.text,
                        wikibase=self.wikibase,
                    )
                    wikipedia_page.extract_and_upload_to_wikicitations()

    @validate_arguments
    def lookup_md5hash(self, md5hash: str):
        """Lookup a md5hash and show the result to the user"""
        console.print(f"Lookup of md5hash {md5hash}")
        wc = WikibaseCrudRead(wikibase=self.wikibase)
        if config.use_cache:
            cache = Cache()
            cache.connect()
            if cache.ssdb:
                cache_result = cache.lookup(key=md5hash)
                if cache_result:
                    console.print(
                        f"CACHE: Found: {cache_result}, see {wc.entity_url(qid=str(cache_result))}",
                        style="green",
                    )
                else:
                    console.print("CACHE: Not found", style="red")
        else:
            console.print("Cache not in use.")
        sparql_result = wc.__get_wcdqids_from_hash__(md5hash=md5hash)
        if sparql_result:
            console.print(
                f"SPARQL: Found: {sparql_result}, see {wc.entity_url(qid=sparql_result[0])}",
                style="green",
            )
        else:
            console.print("SPARQL: Not found", style="red")

    # def print_statistics(self):
    #     self.__calculate_statistics__()
    #     logger.info(
    #         f"A total of {self.total_number_of_references} references "
    #         f"has been processed and {self.total_number_of_hashed_references} "
    #         f"({self.percent_references_hashed_in_total}%) could be hashed on "
    #         f"a total of {len(self.pages)} pages."
    #     )

    def rinse_all_items_and_cache(self):
        """Delete all page and reference items and clear the SSDB cache"""
        wc = WikibaseCrudDelete(wikibase=self.wikibase)
        wc.delete_imported_items()
        if config.use_cache:
            cache = Cache()
            cache.connect()
            cache.flush_database()

    def run(self):
        """This method handles running the bot
        based on the given command line arguments."""
        args = self.__setup_argparse_and_return_args__()
        if args.wikicitations is not None:
            self.wikibase = WikiCitationsWikibase()
        if args.rinse is True:
            self.rinse_all_items_and_cache()
        elif args.import_title is not None:
            logger.info(f"importing title {args.import_title}")
            self.get_and_extract_page_by_title(title=args.import_title)
        elif args.delete_page is not None:
            logger.info("deleting page")
            self.delete_one_page(title=args.delete_page)
        elif args.max_range is not None or args.category is not None:
            logger.info("Importing range of pages")
            self.get_and_extract_pages_by_range(
                max_count=args.max_range, category_title=args.category
            )
        elif args.lookup_md5hash is not None:
            # We strip here to avoid errors caused by spaces
            self.lookup_md5hash(md5hash=args.lookup_md5hash.strip())
        elif args.statistics is not None:
            bot = WcdImportBot(wikibase=SandboxWikibase())
            bot.__gather_and_print_statistics__()
            # DISABLED because it returns 503 now.
            # bot = WcdImportBot(wikibase=WikiCitationsWikibase())
            # bot.__gather_statistics__()
        else:
            console.print("Got no arguments. Try 'python wcdimportbot.py -h' for help")

    # def __calculate_statistics__(self):
    #     """We want to have an overview while the bot is running
    #     about how many references could be imported"""
    #     self.total_number_of_hashed_references = sum(
    #         page.number_of_hashed_references for page in self.pages
    #     )
    #     self.total_number_of_references = sum(
    #         page.number_of_references for page in self.pages
    #     )
    #     if self.total_number_of_references == 0:
    #         self.percent_references_hashed_in_total = 0
    #     else:
    #         self.percent_references_hashed_in_total = int(
    #             self.total_number_of_hashed_references
    #             * 100
    #             / self.total_number_of_references
    #         )
