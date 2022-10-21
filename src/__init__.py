import argparse
import logging
from typing import Optional

from pydantic import validate_arguments
from wikibaseintegrator import wbi_config  # type: ignore
from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore

import config
from src.helpers.console import console
from src.models.cache import Cache
from src.models.exceptions import WikibaseError
from src.models.wikibase import Wikibase
from src.models.wikibase.crud.delete import WikibaseCrudDelete
from src.models.wikibase.crud.read import WikibaseCrudRead
from src.models.wikibase.dictionaries import (
    wcd_externalid_properties,
    wcd_string_properties,
)
from src.models.wikibase.enums import Result, SupportedWikibase
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikibase.wikicitations_wikibase import WikiCitationsWikibase
from src.models.wikimedia.enums import WikimediaSite
from src.models.wikimedia.recent_changes_api.event_stream import EventStream
from src.models.work_queue import WorkQueue
from src.wcd_base_model import WcdBaseModel
from src.wcd_wikibase_model import WcdWikibaseModel

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class WcdImportBot(WcdWikibaseModel):
    """This class controls the import bot

    The language code is the one used by Wikimedia Foundation"""

    cache: Optional[Cache]
    language_code: str = "en"
    event_max_count: int = 0  # 0 means disabled
    page_title: Optional[str]
    percent_references_hashed_in_total: Optional[int]
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    work_queue: Optional[WorkQueue]
    wikidata_qid: str = ""
    testing: bool = False

    def __flush_cache__(self):
        self.__setup_cache__()
        self.cache.flush_database()

    def __gather_and_print_statistics__(self):
        if not self.wikibase:
            self.setup_wikibase()
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

    def __rebuild_cache__(self):
        """Flush and rebuild the cache"""
        self.__flush_cache__()
        if self.cache:
            wcrsandbox = WikibaseCrudRead(wikibase=IASandboxWikibase())
            data = wcrsandbox.__get_all_items_and_hashes__()
            logger.info("Rebuilding the cache")
            count_sandbox = 1
            for entry in data:
                self.__log_to_file__(message=str(entry), file_name="cache-content.log")
                hash_value = entry[1]
                wcdqid = entry[0]
                # logger.debug(f"Inserting {hash_value}:{wcdqid} into the cache")
                self.cache.ssdb.set_value(key=hash_value, value=wcdqid)
                count_sandbox += 1
            wcrswc = WikibaseCrudRead(wikibase=WikiCitationsWikibase())
            data = wcrswc.__get_all_items_and_hashes__()
            logger.info("Rebuilding the cache")
            count_wikicitations = 1
            for entry in data:
                self.__log_to_file__(message=str(entry), file_name="cache-content.log")
                hash_value = entry[1]
                wcdqid = entry[0]
                # logger.debug(f"Inserting {hash_value}:{wcdqid} into the cache")
                self.cache.ssdb.set_value(key=hash_value, value=wcdqid)
                count_wikicitations += 1
            console.print(
                f"Inserted a total of {count_sandbox+count_wikicitations} "
                f"entries into the cache"
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

    Example flush the cache:
    '$ ./wcdimportbot.py --flush-cache'

    Example flush and rebuild the cache:
    '$ ./wcdimportbot.py --rebuild-cache'""",
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
        ),
        parser.add_argument(
            "--flush-cache",
            action="store_true",
            help="Remove all items from the cache",
        ),
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
            "--rebuild-cache",
            action="store_true",
            help="Get all imported items from SPARQL and rebuild the cache",
        ),
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
            action="store_true",
            # TODO revert to defaulting to Wikicitaitons again
            help="Work against Wikicitations. The bot defaults to IASandboxWikibase.",
        )
        parser.add_argument(
            "--worker",
            action="store_true",
            help="Start as worker and consume messages from the work queue.",
        )
        parser.add_argument(
            "--ingestor",
            action="store_true",
            help="Start as ingestor and consume messages from the Wikimedia "
            "Enterprise Page Updates API and publish to the article queue.",
        )
        return parser.parse_args()

    def __setup_cache__(self) -> None:
        """Setup the cache"""
        if not self.cache:
            self.cache = Cache()
            self.cache.connect()

    def __setup_wikibase_integrator_configuration__(
        self,
    ) -> None:
        wbi_config.config["USER_AGENT"] = "wcdimportbot"
        wbi_config.config["WIKIBASE_URL"] = self.wikibase.wikibase_url
        wbi_config.config["MEDIAWIKI_API_URL"] = self.wikibase.mediawiki_api_url
        wbi_config.config["MEDIAWIKI_INDEX_URL"] = self.wikibase.mediawiki_index_url
        wbi_config.config["SPARQL_ENDPOINT_URL"] = self.wikibase.sparql_endpoint_url

    @validate_arguments
    def delete_one_page(self, title: str):
        """Deletes one page from the Wikibase and from the cache"""
        console.print("This has been disabled because we no longer delete items.")
        # logger.debug("delete_one_page: running")
        # with console.status(f"Deleting {title}"):
        #     from src.models.wikimedia.wikipedia.article import (
        #         WikipediaArticle,
        #     )
        #
        #     page = WikipediaArticle(
        #         wikibase=self.wikibase,
        #         language_code=self.language_code,
        #         wikimedia_site=self.wikimedia_site,
        #     )
        #     page.__get_wikipedia_article_from_title__(title=title)
        #     page.__generate_hash__()
        #     # delete from WCD
        #     cache = Cache()
        #     cache.connect()
        #     cache_return = cache.check_page_and_get_wikibase_qid(wikipedia_article=page)
        #     if cache_return.item_qid:
        #         logger.debug(
        #             f"Found {cache_return.item_qid} and trying to delete it now"
        #         )
        #         wc = WikibaseCrudDelete(wikibase=self.wikibase)
        #         result = wc.__delete_item__(item_id=cache_return.item_qid)
        #         if result == Result.SUCCESSFUL:
        #             if page.md5hash is not None:
        #                 cache.delete_key(key=page.md5hash)
        #                 logger.info(f"Deleted {title} from the cache")
        #                 console.print(
        #                     f"Deleted {title} from {self.wikibase.__repr_name__()}"
        #                 )
        #                 return result
        #             else:
        #                 raise ValueError("md5hash was None")
        #         else:
        #             raise WikibaseError("Could not delete the page")
        #     else:
        #         logger.error("Got no item id from the cache")
        #         return Result.FAILED

    @validate_arguments
    def get_and_extract_page_by_title(self):
        """Download and extract the page and the references
        and then upload it to Wikibase. If the page is already
        present in the Wikibase then compare it and all its
        references to make sure we the data is reflecting changes
        made in Wikipedia"""
        if not self.wikibase:
            self.setup_wikibase()
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            wikibase=self.wikibase,
            language_code=self.language_code,
            wikimedia_site=self.wikimedia_site,
            title=self.page_title,
        )
        page.__get_wikipedia_article_from_title__()
        page.extract_and_parse_and_upload_missing_items_to_wikibase()

    @validate_arguments
    def get_and_extract_pages_by_range(
        self, max_count: int = None, category_title: str = None
    ) -> None:
        """
        This method gets all pages in the main namespace up to max_count
        It uses pywikibot
        """
        if not self.wikibase:
            self.setup_wikibase()
        from pywikibot import Category, Site  # type: ignore

        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        if max_count is not None:
            logger.debug(f"Setting max_count to {max_count}")
            self.event_max_count = int(max_count)
        count: int = 0
        # https://stackoverflow.com/questions/59605802/
        # use-pywikibot-to-download-complete-list-of-pages-from-a-mediawiki-server-without
        site = Site(code=self.language_code, fam=str(self.wikimedia_site.value))
        if category_title:
            category_page = Category(title=category_title, source=site)
            for page in category_page.articles(recurse=True):
                if self.event_max_count and count >= self.event_max_count:
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
                    wikipedia_article = WikipediaArticle(
                        wikibase=self.wikibase,
                        language_code=self.language_code,
                        latest_revision_date=page.editTime(),
                        latest_revision_id=page.latest_revision_id,
                        page_id=page.pageid,
                        title=str(page.title()),
                        wikimedia_site=self.wikimedia_site,
                        wikitext=page.text,
                    )
                    wikipedia_article.extract_and_parse_and_upload_missing_items_to_wikibase()
        else:
            for page in site.allpages(namespace=0):
                if count >= self.event_max_count:
                    break
                # page: Page = page
                if not page.isRedirectPage():
                    count += 1
                    # console.print(count)
                    logger.info(f"{page.pageid} {page.page_title()}")
                    # raise DebugExit()
                    wikipedia_article = WikipediaArticle(
                        language_code=self.language_code,
                        latest_revision_date=page.editTime(),
                        latest_revision_id=page.latest_revision_id,
                        page_id=page.pageid,
                        title=str(page.page_title()),
                        wikimedia_site=self.wikimedia_site,
                        wikitext=page.text,
                        wikibase=self.wikibase,
                    )
                    wikipedia_article.extract_and_parse_and_upload_missing_items_to_wikibase()

    @validate_arguments
    def lookup_md5hash(self, md5hash: str):
        """Lookup a md5hash and show the result to the user"""
        if not self.wikibase:
            self.setup_wikibase()
        console.print(f"Lookup of md5hash {md5hash}")
        wc = WikibaseCrudRead(wikibase=self.wikibase)
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
            raise Exception("no ssdb in the cache instance")
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

    @staticmethod
    def rinse_all_items_and_cache():
        """Delete all page and reference items and clear the SSDB cache"""
        console.print("This has been disabled because we no longer delete items.")
        # wc = WikibaseCrudDelete(wikibase=self.wikibase)
        # wc.delete_imported_items()
        # self.__flush_cache__()

    def run(self):
        """This method handles running the bot
        based on the given command line arguments."""
        args = self.__setup_argparse_and_return_args__()
        if args.wikicitations:
            self.wikibase = WikiCitationsWikibase()
        if args.rinse:
            self.rinse_all_items_and_cache()
        elif args.rebuild_cache:
            self.__rebuild_cache__()
        elif args.flush_cache:
            self.__flush_cache__()
        elif args.import_title:
            logger.info(f"importing title {args.import_title}")
            self.page_title = args.import_title
            self.get_and_extract_page_by_title()
        elif args.delete_page:
            logger.info("deleting page")
            self.delete_one_page(title=args.delete_page)
        elif args.max_range or args.category:
            logger.info("Importing range of pages")
            self.get_and_extract_pages_by_range(
                max_count=args.max_range, category_title=args.category
            )
        elif args.lookup_md5hash:
            # We strip here to avoid errors caused by spaces
            self.lookup_md5hash(md5hash=args.lookup_md5hash.strip())
        elif args.statistics:
            bot = WcdImportBot(wikibase=IASandboxWikibase())
            bot.__gather_and_print_statistics__()
            # DISABLED because it returns 503 now.
            bot = WcdImportBot(wikibase=WikiCitationsWikibase())
            bot.__gather_and_print_statistics__()
        elif args.worker:
            if not self.wikibase:
                self.setup_wikibase()
            work_queue = WorkQueue(wikibase=self.wikibase)
            console.print("Starting worker")
            work_queue.listen_to_queue()
        elif args.ingestor:
            if not self.wikibase:
                self.setup_wikibase()
            event_stream = EventStream(wikibase=self.wikibase)
            console.print("Starting ingestor")
            event_stream.start_consuming()
        else:
            console.print("Got no arguments. Try 'python wcdimportbot.py -h' for help")

    def __receive_workloads__(self):
        self.work_queue = WorkQueue(wikibase=self.wikibase, testing=self.testing)
        self.work_queue.listen_to_queue()

    def get_and_extract_page_by_wdqid(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            wikibase=self.wikibase,
            language_code=self.language_code,
            wikimedia_site=self.wikimedia_site,
            wdqid=self.wikidata_qid,
        )
        page.__get_wikipedia_article_from_wdqid__()
        page.extract_and_parse_and_upload_missing_items_to_wikibase()
