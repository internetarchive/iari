import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Any, List, Optional
from urllib.parse import urlparse

from pydantic import validate_arguments, validator
from tld import get_fld
from tld.exceptions import TldBadUrl

import config
from src import WikimediaSite
from src.helpers.template_extraction import extract_templates_and_params
from src.models.exceptions import (
    AmbiguousDateError,
    MissingInformationError,
    MoreThanOneNumberError,
)
from src.models.person import Person
from src.models.return_.cache_return import CacheReturn
from src.models.return_.wikibase_return import WikibaseReturn
from src.models.wcd_item import WcdItem
from src.models.wikimedia.wikipedia.reference.english.google_books import (
    GoogleBooks,
    GoogleBooksSchema,
)
from src.models.wikimedia.wikipedia.reference.enums import (
    EnglishWikipediaTemplatePersonRole,
)

logger = logging.getLogger(__name__)

# We use marshmallow here because pydantic did not seem to support optional alias fields.
# https://github.com/samuelcolvin/pydantic/discussions/3855


class WikipediaReference(WcdItem):
    """This models any page_reference on a Wikipedia page

    As we move to support more than one Wikipedia this model should be generalized further.

    Do we want to merge page + pages into a string property like in Wikidata?
    How do we handle parse errors? In a file log? Should we publish the log for Wikipedians to fix?

    Validation works better with pydantic so we validate when creating this object

    Support date ranges like "May-June 2011"? See https://stackoverflow.com/questions/10340029/
    """

    authors_list: Optional[List[Person]]
    detected_archive_of_archive_url: Optional[
        Any
    ]  # KnownArchiveUrl: we don't type this because of circular imports
    detected_archive_of_url: Optional[
        Any
    ]  # KnownArchiveUrl: we don't type this because of circular imports
    editors_list: Optional[List[Person]]
    first_lasts: Optional[List]
    first_level_domain_of_archive_url: Optional[str]
    first_level_domain_of_url: Optional[str]
    first_level_domain_of_url_hash: Optional[str]
    website_item: Optional[WcdItem]
    # google_books: Optional[GoogleBooks]
    # google_books_id: Optional[str]
    hosts_list: Optional[List[Person]]
    interviewers_list: Optional[List[Person]]
    isbn_10: Optional[str]
    isbn_13: Optional[str]
    internet_archive_id: Optional[str]
    md5hash: Optional[str]
    numbered_first_lasts: Optional[List]
    orcid: Optional[str]  # Is this present in the wild?
    persons_without_role: Optional[List[Person]]
    template_name: str  # We use this to keep track of which template the information came from
    translators_list: Optional[List[Person]]
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA

    # These are all the parameters in the supported references
    #######################
    # Names
    #######################
    first1: Optional[str]
    first2: Optional[str]
    first3: Optional[str]
    first4: Optional[str]
    first5: Optional[str]
    first6: Optional[str]
    first: Optional[str]
    last1: Optional[str]
    last2: Optional[str]
    last3: Optional[str]
    last4: Optional[str]
    last5: Optional[str]
    last6: Optional[str]
    last: Optional[str]

    #######################
    # Author first/given (equal)
    #######################
    author_given: Optional[str]
    author_given1: Optional[str]
    author_given2: Optional[str]
    author_given3: Optional[str]
    author_given4: Optional[str]
    author_given5: Optional[str]
    author_first: Optional[str]
    author_first1: Optional[str]
    author_first2: Optional[str]
    author_first3: Optional[str]
    author_first4: Optional[str]
    author_first5: Optional[str]

    #######################
    # Author last/surname (equal)
    #######################
    author_surname: Optional[str]
    author_surname1: Optional[str]
    author_surname2: Optional[str]
    author_surname3: Optional[str]
    author_surname4: Optional[str]
    author_surname5: Optional[str]
    author_last: Optional[str]
    author_last1: Optional[str]
    author_last2: Optional[str]
    author_last3: Optional[str]
    author_last4: Optional[str]
    author_last5: Optional[str]

    # Author
    author1_first: Optional[str]
    author1_last: Optional[str]
    author1_link: Optional[str]
    author2_first: Optional[str]
    author2_last: Optional[str]
    author2_link: Optional[str]
    author3_first: Optional[str]
    author3_last: Optional[str]
    author3_link: Optional[str]
    author4_first: Optional[str]
    author4_last: Optional[str]
    author4_link: Optional[str]
    author5_first: Optional[str]
    author5_last: Optional[str]
    author5_link: Optional[str]
    author: Optional[str]
    author_link1: Optional[str]
    author_link2: Optional[str]
    author_link3: Optional[str]
    author_link4: Optional[str]
    author_link5: Optional[str]
    author_link: Optional[str]
    author_mask1: Optional[str]
    author_mask2: Optional[str]
    author_mask3: Optional[str]
    author_mask4: Optional[str]
    author_mask5: Optional[str]
    author_mask: Optional[str]

    #######################
    # Editor
    #######################
    editor1_first: Optional[str]
    editor1_last: Optional[str]
    editor1_link: Optional[str]
    editor2_first: Optional[str]
    editor2_last: Optional[str]
    editor2_link: Optional[str]
    editor3_first: Optional[str]
    editor3_last: Optional[str]
    editor3_link: Optional[str]
    editor4_first: Optional[str]
    editor4_last: Optional[str]
    editor4_link: Optional[str]
    editor5_first: Optional[str]
    editor5_last: Optional[str]
    editor5_link: Optional[str]
    editor: Optional[str]
    editor_first1: Optional[str]
    editor_first2: Optional[str]
    editor_first3: Optional[str]
    editor_first4: Optional[str]
    editor_first5: Optional[str]
    editor_first: Optional[str]
    editor_last1: Optional[str]
    editor_last2: Optional[str]
    editor_last3: Optional[str]
    editor_last4: Optional[str]
    editor_last5: Optional[str]
    editor_last: Optional[str]
    editor_link1: Optional[str]
    editor_link2: Optional[str]
    editor_link3: Optional[str]
    editor_link4: Optional[str]
    editor_link5: Optional[str]
    editor_link: Optional[str]
    editor_mask1: Optional[str]
    editor_mask2: Optional[str]
    editor_mask3: Optional[str]
    editor_mask4: Optional[str]
    editor_mask5: Optional[str]
    editor_mask: Optional[str]

    #######################
    # Translator
    #######################
    translator_first1: Optional[str]
    translator_first2: Optional[str]
    translator_first3: Optional[str]
    translator_first4: Optional[str]
    translator_first5: Optional[str]
    translator_first: Optional[str]
    translator_last1: Optional[str]
    translator_last2: Optional[str]
    translator_last3: Optional[str]
    translator_last4: Optional[str]
    translator_last5: Optional[str]
    translator_last: Optional[str]
    translator_link1: Optional[str]
    translator_link2: Optional[str]
    translator_link3: Optional[str]
    translator_link4: Optional[str]
    translator_link5: Optional[str]
    translator_link: Optional[str]
    translator_mask1: Optional[str]
    translator_mask2: Optional[str]
    translator_mask3: Optional[str]
    translator_mask4: Optional[str]
    translator_mask5: Optional[str]
    translator_mask: Optional[str]

    #######################
    # Interviewer
    #######################
    interviewer_given: Optional[str]
    interviewer_first: Optional[str]
    interviewer_surname: Optional[str]
    interviewer_last: Optional[str]

    #######################
    # Host
    #######################
    host: Optional[str]
    host1: Optional[str]
    host2: Optional[str]
    host3: Optional[str]
    host4: Optional[str]
    host5: Optional[str]

    #######################
    # Boolean switches
    #######################
    display_authors: Optional[str]  # we can ignore this one
    display_editors: Optional[str]  # we can ignore this one
    display_translators: Optional[str]  # we can ignore this one
    display_subjects: Optional[str]  # we can ignore this one

    # Others
    access_date: Optional[datetime]
    agency: Optional[str]  # what is this?
    archive_date: Optional[datetime]
    archive_url: Optional[str]
    arxiv: Optional[str]
    asin: Optional[str]  # what is this?
    asin_tld: Optional[str]
    at: Optional[str]  # what is this?
    bibcode: Optional[str]
    bibcode_access: Optional[str]
    biorxiv: Optional[str]
    book_title: Optional[str]
    chapter: Optional[str]
    chapter_format: Optional[str]
    chapter_url: Optional[str]
    chapter_url_access: Optional[str]
    citeseerx: Optional[str]
    news_class: Optional[str]  # used in cite arxiv
    conference: Optional[str]
    conference_url: Optional[str]
    date: Optional[datetime]
    degree: Optional[str]
    department: Optional[str]
    doi: Optional[str]
    doi_access: Optional[str]
    doi_broken_date: Optional[datetime]
    edition: Optional[str]
    eissn: Optional[str]
    encyclopedia: Optional[str]
    eprint: Optional[str]
    format: Optional[str]
    hdl: Optional[str]
    hdl_access: Optional[str]
    id: Optional[str]  # where does this come from?
    isbn: Optional[str]
    ismn: Optional[str]
    issn: Optional[str]
    issue: Optional[str]
    jfm: Optional[str]
    journal: Optional[str]
    jstor: Optional[str]
    jstor_access: Optional[str]
    language: Optional[str]  # do we want to parse this?
    lccn: Optional[str]
    location: Optional[str]
    mode: Optional[str]  # what is this?
    mr: Optional[str]
    name_list_style: Optional[str]
    no_pp: Optional[str]
    oclc: Optional[str]
    ol: Optional[str]  # what is this?
    ol_access: Optional[str]
    orig_date: Optional[datetime]
    orig_year: Optional[datetime]
    osti: Optional[str]  # what is this?
    osti_access: Optional[str]
    others: Optional[str]  # what is this?
    page: Optional[str]
    pages: Optional[str]
    pmc: Optional[str]
    pmc_embargo_date: Optional[datetime]
    pmid: Optional[str]
    postscript: Optional[str]  # what is this?
    publication_date: Optional[datetime]
    publication_place: Optional[str]
    publisher: Optional[str]
    quote: Optional[str]  # do we want to store this?
    quote_page: Optional[str]
    quote_pages: Optional[str]
    ref: Optional[str]
    registration: Optional[str]  # what is this?
    rfc: Optional[str]  # what is this?
    s2cid: Optional[str]
    s2cid_access: Optional[str]
    sbn: Optional[str]
    script_chapter: Optional[str]
    script_quote: Optional[str]
    script_title: Optional[str]
    series: Optional[str]
    ssrn: Optional[str]
    subject: Optional[str]
    subject_mask: Optional[str]
    subscription: Optional[str]
    # title: Optional[str]
    title_link: Optional[str]
    trans_chapter: Optional[str]  # this is a translation of a chapter
    trans_quote: Optional[str]  # this is a translation of a quote
    trans_title: Optional[str]  # this is a translation of a title
    type: Optional[str]  # what is this?
    url: Optional[str]
    url_access: Optional[str]
    url_status: Optional[str]
    via: Optional[str]  # what is this?
    volume: Optional[str]
    website: Optional[str]
    work: Optional[str]
    year: Optional[datetime]
    zbl: Optional[str]  # what is this?

    #######################
    # Deprecated parameters
    #######################
    # We ignore these
    # cite news
    lay_date: Optional[str]
    lay_format: Optional[str]
    lay_source: Optional[str]
    lay_url: Optional[str]
    transcripturl: Optional[str]

    # Numbered parameters
    first_parameter: Optional[str]  # 1
    second_parameter: Optional[str]  # 2

    # Fields found in the wild
    df: Optional[str]
    magazine: Optional[str]
    newspaper: Optional[str]
    author1: Optional[str]
    author2: Optional[str]
    author3: Optional[str]
    author4: Optional[str]
    author5: Optional[str]
    author6: Optional[str]
    author7: Optional[str]
    author8: Optional[str]
    author9: Optional[str]
    author10: Optional[str]
    editor1: Optional[str]
    editor2: Optional[str]
    editor3: Optional[str]
    editor4: Optional[str]
    editor5: Optional[str]
    number: Optional[str]
    first7: Optional[str]
    first8: Optional[str]
    first9: Optional[str]
    first10: Optional[str]
    first11: Optional[str]
    first12: Optional[str]
    first13: Optional[str]
    first14: Optional[str]
    last7: Optional[str]
    last8: Optional[str]
    last9: Optional[str]
    last10: Optional[str]
    last11: Optional[str]
    last12: Optional[str]
    last13: Optional[str]
    last14: Optional[str]
    message_id: Optional[str]
    newsgroup: Optional[str]
    archive_format: Optional[str]
    time: Optional[datetime]
    interviewer: Optional[str]
    medium: Optional[str]
    contribution: Optional[str]
    vauthors: Optional[
        str
    ]  # this appears in cite journal and is used to specify authors_list using the Vancouver system
    authors: Optional[str]
    place: Optional[str]
    lang: Optional[str]
    periodical: Optional[str]

    @property
    def has_first_level_domain_url_hash(self) -> bool:
        return bool(self.first_level_domain_of_url_hash is not None)

    @property
    def has_hash(self) -> bool:
        return bool(self.md5hash is not None)

    # @property
    # def isodate(self) -> str:
    #     if self.publication_date is not None:
    #         return datetime.strftime(self.publication_date, "%Y-%m-%d")
    #     elif self.date is not None:
    #         return datetime.strftime(self.date, "%Y-%m-%d")
    #     elif self.year is not None:
    #         return datetime.strftime(self.year, "%Y-%m-%d")
    #     else:
    #         raise ValueError(
    #             f"missing publication date, in template {self.template_name}, see {self.dict()}"
    #         )

    @property
    def template_url(self) -> str:
        return f"https://en.wikipedia.org/wiki/Template:{self.template_name}"

    @property
    def wikibase_url(self) -> str:
        if not self.wikibase:
            raise MissingInformationError("self.wikibase was None")
        if not self.return_:
            raise MissingInformationError("self.return_ was None")
        return f"{self.wikibase.wikibase_url}" f"wiki/Item:{self.return_.item_qid}"

    @validate_arguments
    def check_and_upload_reference_item_to_wikibase_if_missing(self) -> None:
        """Check and upload reference item to Wikibase if missing and return an
        updated reference with the attribute return_ set"""
        logger.debug(
            "__check_and_upload_reference_item_to_wikicitations_if_missing__: Running"
        )
        self.get_wcdqid_from_cache()
        if self.return_:
            if not self.return_.item_qid:
                logger.info(
                    f"Could not find reference with {self.md5hash} in the cache"
                )
                self.upload_reference_and_insert_in_the_cache_if_enabled()
        else:
            raise MissingInformationError("self.return_ was None")

    def __clean_wiki_markup_from_strings__(self):
        """We clean away [[ and ]]
        For now we only clean self.publisher"""
        if self.publisher:
            if "[[" in self.publisher and "|" not in self.publisher:
                self.publisher = self.publisher.replace("[[", "").replace("]]", "")
            if "[[" in self.publisher and "|" in self.publisher:
                """We save the first part of the string only
                e.g. [[University of California, Berkeley|Berkeley]]"""
                self.publisher = (
                    self.publisher.replace("[[", "").replace("]]", "").split("|")[0]
                )

    def __detect_archive_urls__(self):
        """Try to detect if self.url contains first level
        domain from a known web archiver"""
        logger.debug("__detect_archive_urls__: Running")
        from src.models.wikibase.enums import KnownArchiveUrl

        # ARCHIVE_URL
        if self.first_level_domain_of_archive_url:
            logger.debug("__detect_archive_urls__: Working on self.archive_url")
            try:
                logger.debug(
                    f"Trying to detect archive from {self.first_level_domain_of_archive_url}"
                )
                self.detected_archive_of_archive_url = KnownArchiveUrl(
                    self.first_level_domain_of_archive_url
                )
            except ValueError:
                self.__log_to_file__(
                    message=f"No archive detected for {self.archive_url}",
                    file_name="undetected_archive.log",
                )

        # URL
        if self.first_level_domain_of_url:
            try:
                logger.debug(
                    f"Trying to detect archive from {self.first_level_domain_of_url}"
                )
                self.detected_archive_of_url = KnownArchiveUrl(
                    self.first_level_domain_of_url
                )
            except ValueError:
                # We don't log this because it would clog the
                # log file very quickly and not yield anything useful
                pass

    # DEPRECATED since 2.1.0-alpha3
    # def __detect_google_books_id__(self):
    #     """We detect GOOGLE_BOOKS_ID to populate the property later
    #     Example: https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431
    #     NOTE: we don't parse the page number for now"""
    #     if (
    #         self.first_level_domain_of_url
    #         and "google." in self.first_level_domain_of_url
    #     ):
    #         if self.url and "/books.google." in self.url:
    #             query = str(urlparse(self.url).query)
    #             parsed_query = parse_qs(query)
    #             if parsed_query and "id" in parsed_query.keys():
    #                 self.google_books_id = parsed_query["id"][0]
    #             else:
    #                 raise ValueError(
    #                     f"could not extract query from {self.url} or no id found in the url"
    #                 )

    def __detect_internet_archive_id__(self):
        """We detect INTERNET_ARCHIVE_ID to populate the property later
        Example: https://archive.org/details/catalogueofshipw0000wils/"""
        if (
            self.first_level_domain_of_url
            and self.first_level_domain_of_url == "archive.org"
        ):
            if self.url and "/details/" in self.url:
                path = str(urlparse(self.url).path)
                if path:
                    self.internet_archive_id = path.split("/")[2]
                else:
                    raise ValueError(f"could not extract path from {self.url}")

    def __extract_first_level_domain__(self):
        logger.info("Extracting first level domain from self.url and self.archive_url")
        if self.url is not None:
            self.first_level_domain_of_url = self.__get_first_level_domain__(
                url=self.url
            )
        if self.archive_url is not None:
            self.first_level_domain_of_archive_url = self.__get_first_level_domain__(
                url=self.archive_url
            )

    @staticmethod
    @validate_arguments
    def __find_number__(string: str) -> Optional[int]:
        """Find all numbers in a string"""
        # logger.debug(f"Trying to find numbers in: {string}.")
        numbers = re.findall(r"\d+", string)
        if len(numbers) == 1:
            return int(numbers[0])
        elif len(numbers) > 1:
            raise MoreThanOneNumberError(f"found {numbers}")
        else:
            # logger.debug(f"Found no numbers.")
            return None

    def __generate_first_level_domain_hash__(self):
        """This is used as hash for all website items"""
        if self.first_level_domain_of_url is not None:
            str2hash = self.first_level_domain_of_url
            self.first_level_domain_of_url_hash = hashlib.md5(
                f'{self.wikibase.title}{str2hash.replace(" ", "").lower()}'.encode()
            ).hexdigest()

    def __generate_hashes__(self):
        """Generate hashes for both website and reference items"""
        if not self.wikibase:
            raise MissingInformationError("self.wikibase was None")
        self.__generate_reference_hash__()
        self.__generate_first_level_domain_hash__()

    def __generate_reference_hash__(self):
        """We generate a md5 hash of the page_reference as a unique identifier for any given page_reference in a Wikipedia page
        We choose md5 because it is fast https://www.geeksforgeeks.org/difference-between-md5-and-sha1/"""
        str2hash = None
        # TODO decide if we really trust doi to be unique.
        #  See https://www.wikidata.org/wiki/Property_talk:P356
        # In WD there are as of 2022-07-11 25k violations here.
        # Most are due to bad data at PubMed
        # see https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P356#Unique_value
        # and https://twitter.com/DennisPriskorn/status/1546475347851591680
        if self.wikidata_qid:
            # This is the external id we trust the most.
            str2hash = self.wikidata_qid
        if self.doi:
            str2hash = self.doi
        elif self.pmid:
            str2hash = self.pmid
        elif self.isbn:
            # We strip the dashes before hashing
            str2hash = self.isbn.replace("-", "")
        # TODO decide if we really trust oclc to be unique
        # See https://www.wikidata.org/wiki/Property_talk:P243
        elif self.oclc:
            str2hash = self.oclc
        elif self.url:
            if config.include_url_in_hash_algorithm:
                str2hash = self.url
        # elif self.first_parameter:
        #     if config.include_url_in_hash_algorithm:
        #         str2hash = self.first_parameter

        # DISABLED template specific hashing for now because it is error
        # prone and does not make it easy to avoid duplicates
        # For example a news article might be cited with the publication date in one place but not in another.
        # If we include the publication date in the hash we will end up with a duplicate in Wikibase.
        # if self.template_name == "cite av media":
        #     """{{cite AV media |people= |date= |title= |trans-title= |type=
        #     |language= |url= |access-date= |archive-url= |archive-date=
        #     |format= |time= |location= |publisher= |id= |isbn= |oclc= |quote= |ref=}}"""
        #     # https://en.wikipedia.org/wiki/Template:Cite_AV_media
        #     if self.doi is None:
        #         if self.isbn is None:
        #             str2hash = self.__hash_based_on_title_and_date__()
        #         else:
        #             str2hash = self.isbn
        #     else:
        #         str2hash = self.doi
        # elif self.template_name == "cite book":
        #     if self.isbn is None:
        #         str2hash = self.__hash_based_on_title_and_publisher_and_date__()
        #     else:
        #         str2hash = self.isbn
        # elif self.template_name == "cite journal":
        #     if self.doi is None:
        #         # Fallback first to PMID
        #         if self.pmid is None:
        #             str2hash = self.__hash_based_on_title_and_date__()
        #         else:
        #             str2hash = self.pmid
        #     else:
        #         str2hash = self.doi
        # elif self.template_name == "cite magazine":
        #     """{{cite magazine |last= |first= |date= |title= |url=
        #     |magazine= |location= |publisher= |access-date=}}"""
        #     if self.doi is None:
        #         #  clean URL first?
        #         if (self.title) is not None:
        #             str2hash = self.title + self.isodate
        #         else:
        #             raise ValueError(
        #                 f"did not get what we need to generate a hash, {self.dict()}"
        #             )
        #     else:
        #         str2hash = self.doi
        # elif self.template_name == "cite news":
        #     if self.doi is None:
        #         #  clean URL first?
        #         if (self.title) is not None:
        #             str2hash = self.title + self.isodate
        #         else:
        #             raise ValueError(
        #                 f"did not get what we need to generate a hash, {self.dict()}"
        #             )
        #     else:
        #         str2hash = self.doi
        # elif self.template_name == "cite web":
        #     if self.doi is None:
        #         # Many of these references lead to pages without any publication
        #         # dates unfortunately. e.g. https://www.billboard.com/artist/chk-chk-chk-2/chart-history/tlp/
        #         #  clean URL first?
        #         if self.url is not None:
        #             str2hash = self.url
        #         else:
        #             raise ValueError(
        #                 f"did not get what we need to generate a hash, {self.dict()}"
        #             )
        #     else:
        #         str2hash = self.doi
        # elif self.template_name == "url":
        #     """Example:{{url|chkchkchk.net}}"""
        #     if self.doi is None:
        #         #  clean URL first?
        #         if self.first_parameter is not None:
        #             str2hash = self.first_parameter
        #         else:
        #             raise ValueError(
        #                 f"did not get what we need to generate a hash, {self.dict()}"
        #             )
        #     else:
        #         str2hash = self.doi
        # else:
        #     # Do we want a generic fallback?
        #     pass
        if str2hash is not None:
            self.md5hash = hashlib.md5(
                f'{self.wikibase.title}{str2hash.replace(" ", "").lower()}'.encode()
            ).hexdigest()
            logger.debug(self.md5hash)
        else:
            self.md5hash = ""
            logger.warning(
                f"hashing not possible for this instance of {self.template_name} "
                f"because no identifier or url or first parameter was found "
                f"or they were turned of in config.py."
            )

    @validate_arguments
    def __get_first_level_domain__(self, url: str) -> Optional[str]:
        logger.debug("__get_first_level_domain__: Running")
        try:
            logger.debug(f"Trying to get FLD from {url}")
            fld = get_fld(url)
            if fld:
                logger.debug(f"Found FLD: {fld}")
            return fld
        except TldBadUrl:
            """The library does not support archive.org URLs"""
            if "web.archive.org" in url:
                return "archive.org"
            else:
                message = f"Bad url {url} encountered"
                logger.warning(message)
                self.__log_to_file__(
                    message=str(message), file_name="url_exceptions.log"
                )
                return None

    @validate_arguments
    def __get_numbered_person__(
        self,
        attributes: List[str],
        number: int,
        role: EnglishWikipediaTemplatePersonRole = None,
        search_string: str = None,
    ) -> Optional[Person]:
        """This functions gets all types of numbered persons,
        both those with roles and those without"""
        # First handle persons with a role
        if role is not None and search_string is not None:
            # Collect all attributes
            matching_attributes = [
                attribute
                for attribute in attributes
                if search_string in attribute and getattr(self, attribute) is not None
            ]
            # Find the attributes with the correct number
            found_attributes = [
                attribute
                for attribute in matching_attributes
                if self.__find_number__(attribute) == number
            ]
            if len(found_attributes) > 0:
                person = Person(role=role, number_in_sequence=number)
                for attribute in found_attributes:
                    # logger.debug(attribute, getattr(self, attribute))
                    # Handle attributes with a number in the end. E.g. "author_link1"
                    if attribute == search_string + str(number):
                        person.name_string = getattr(self, search_string + str(number))
                    if attribute == search_string + "_link" + str(number):
                        person.link = getattr(
                            self, search_string + "_link" + str(number)
                        )
                    if attribute == search_string + "_mask" + str(number):
                        person.mask = getattr(
                            self, search_string + "_mask" + str(number)
                        )
                    if attribute == search_string + "_first" + str(number):
                        person.given = getattr(
                            self, search_string + "_first" + str(number)
                        )
                    if attribute == search_string + "_last" + str(number):
                        person.surname = getattr(
                            self, search_string + "_last" + str(number)
                        )
                    # str(number) after author. E.g. "author1_link"
                    if attribute == search_string + str(number) + "_link":
                        person.link = getattr(
                            self, search_string + str(number) + "_link"
                        )
                    if attribute == search_string + str(number) + "_mask":
                        person.mask = getattr(
                            self, search_string + str(number) + "_mask"
                        )
                    if attribute == search_string + str(number) + "_first":
                        person.given = getattr(
                            self, search_string + str(number) + "_first"
                        )
                    if attribute == search_string + str(number) + "_last":
                        person.surname = getattr(
                            self, search_string + str(number) + "_last"
                        )
                # Guard against empty person objects being returned
                if (
                    person.given and person.surname
                ) is not None or person.name_string is not None:
                    person.number_in_sequence = number
                    return person
                else:
                    logger.debug(
                        f"Discarded {person} because it did not have both given- and surnames or name_string"
                    )
                    return None
            else:
                return None
        else:
            # Support cite journal first[1-12] and last[1-12]
            if self.first_lasts is None:
                self.first_lasts = [
                    attribute
                    for attribute in attributes
                    if ("first" in attribute or "last" in attribute)
                    and getattr(self, attribute) is not None
                ]
            logger.debug(f"{len(self.first_lasts)} first lasts found.")
            if self.numbered_first_lasts is None:
                self.numbered_first_lasts = [
                    attribute
                    for attribute in self.first_lasts
                    if self.__find_number__(attribute) == number
                ]
            logger.debug(
                f"{len(self.numbered_first_lasts)} numbered first lasts found with number {number}."
            )
            if len(self.numbered_first_lasts) > 0:
                person = Person(
                    role=EnglishWikipediaTemplatePersonRole.UNKNOWN,
                )
                for attribute in self.numbered_first_lasts:
                    # logger.debug(attribute, getattr(self, attribute))
                    first = "first" + str(number)
                    last = "last" + str(number)
                    if attribute == first:
                        person.given = getattr(self, first)
                    if attribute == last:
                        person.surname = getattr(self, last)
                # Guard against empty person objects being returned
                if (
                    person.given and person.surname
                ) is not None or person.name_string is not None:
                    person.number_in_sequence = number
                    return person
                else:
                    logger.debug(
                        f"Discarded {person} because it did not have both given- and surnames or name_string"
                    )
                    return None
            else:
                return None

    @validate_arguments
    def __get_numbered_persons__(
        self,
        attributes: List[str],
        role: EnglishWikipediaTemplatePersonRole = None,
        search_string: str = None,
    ) -> List[Person]:
        """This is just a helper function to call __get_numbered_person__"""
        # Mypy warns that the following could add None to the list,
        # but that cannot happen.
        maybe_persons = [
            self.__get_numbered_person__(
                attributes=attributes,
                number=number,
                role=role,
                search_string=search_string,
            )
            for number in range(1, 14)
        ]
        # We discard all None-values here to placate mypy
        return [i for i in maybe_persons if i]

    # def __hash_based_on_title_and_date__(self):
    #     logger.debug("__hash_based_on_title_and_date__: running")
    #     if self.title is not None:
    #         return self.title + self.isodate
    #     else:
    #         raise ValueError(
    #             f"did not get what we need to generate a hash, {self.dict()}"
    #         )
    #
    # def __hash_based_on_title_and_journal_and_date__(self):
    #     logger.debug("__hash_based_on_title_and_journal_and_date__: running")
    #     if (self.title and self.journal) is not None:
    #         return self.title + self.journal + self.isodate
    #     else:
    #         raise ValueError(
    #             f"did not get what we need to generate a hash, {self.dict()}"
    #         )
    #
    # def __hash_based_on_title_and_publisher_and_date__(self):
    #     logger.debug("__hash_based_on_title_and_publisher_and_date__: running")
    #     if (self.title and self.publisher) is not None:
    #         return self.title + self.publisher + self.isodate
    #     else:
    #         raise ValueError(
    #             f"did not get what we need to generate a hash, {self.dict()}"
    #         )

    def __merge_date_into_publication_date__(self):
        """Handle the possibly ambiguous self.date field"""
        if self.date and self.publication_date:
            if self.date != self.publication_date:
                raise AmbiguousDateError(
                    f"got both a date and a publication_date and they differ"
                )
        if self.date and not self.publication_date:
            # Assuming date is the publication date
            self.publication_date = self.date
            logger.debug("Assumed date == publication_data")

    def __merge_lang_into_language__(self):
        """We merge lang into language or log if both are populated"""
        if self.lang and not self.language:
            self.language = self.lang
        elif self.lang and self.language:
            self.__log_to_file__(
                message=f"both lang: '{self.lang}' and language: '{self.language} is populated",
                file_name="lang.log",
            )

    def __merge_place_into_location__(self):
        """Merge place into location or log if both are populated"""
        if self.place and not self.location:
            self.location = self.place
        elif self.place and self.location:
            self.__log_to_file__(
                message=f"both place: '{self.place}' and location: '{self.location} is populated",
                file_name="place.log",
            )

    def __parse_first_parameter__(self) -> None:
        """We parse the first parameter which has different meaning
        depending on the template in question"""
        if self.template_name in ("cite q", "citeq"):
            # We assume that the first parameter is the Wikidata QID
            if self.first_parameter:
                if self.first_parameter[:1] in ("q", "Q"):
                    self.wikidata_qid = self.first_parameter
                else:
                    logger.warning(
                        f"First parameter '{self.first_parameter}' "
                        f"of {self.template_name} was not a valid "
                        f"WD QID"
                    )
        elif self.template_name == "url":
            # crudely detect if url with scheme in first_parameter
            if self.first_parameter:
                if "://" in self.first_parameter:
                    self.url = self.first_parameter
                else:
                    logger.warning(
                        f"'{self.first_parameter}' was not recognized as a URL"
                    )
                    self.url = ""
        elif self.template_name == "isbn":
            self.isbn = self.first_parameter

    # DEPRECATED since 2.1.0-alpha3
    # def __parse_google_books_template__(self):
    #     """Parse the Google Books template that sometimes appear in self.url
    #     and save the result in self.google_books and generate the URL
    #     and store it in self.url"""
    #     logger.debug("__parse_google_books__: Running")
    #     template_tuples = extract_templates_and_params(self.url, True)
    #     if template_tuples:
    #         logger.info("Found Google books template")
    #         for _template_name, content in template_tuples:
    #             google_books: GoogleBooks = GoogleBooksSchema().load(content)
    #             google_books.wikibase = self.wikibase
    #             google_books.finish_parsing()
    #             self.url = google_books.url
    #             self.google_books_id = google_books.id
    #             self.google_books = google_books

    def __parse_isbn__(self) -> None:
        if self.isbn is not None:
            # Replace spaces with dashes to follow the ISBN standard
            self.isbn = self.isbn.replace(" ", "-")
            stripped_isbn = self.isbn.replace("-", "")
            if stripped_isbn in ["", " "]:
                self.isbn = None
            else:
                if len(stripped_isbn) == 13:
                    self.isbn_13 = self.isbn
                elif len(stripped_isbn) == 10:
                    self.isbn_10 = self.isbn
                else:
                    message = (
                        f"isbn: {self.isbn} was not "
                        f"10 or 13 chars long after "
                        f"removing the dashes"
                    )
                    logger.warning(message)
                    self.__log_to_file__(
                        message=message, file_name="isbn_exceptions.log"
                    )

    @validate_arguments
    def __parse_known_role_persons__(
        self, attributes: List[str], role: EnglishWikipediaTemplatePersonRole
    ) -> List[Person]:
        persons = []
        person_without_number = [
            attribute
            for attribute in attributes
            if self.__find_number__(attribute) is None and str(role.value) in attribute
        ]
        if len(person_without_number) > 0:
            person = Person(role=role)
            link = role.value + "_link"
            mask = role.value + "_mask"
            first = role.value + "_first"
            last = role.value + "_last"
            for attribute in person_without_number:
                # print(attribute, getattr(self, attribute))
                if attribute == role.value:
                    person.name_string = getattr(self, str(role.value))
                if attribute == link:
                    person.link = getattr(self, link)
                if attribute == mask:
                    person.mask = getattr(self, mask)
                if attribute == first:
                    person.given = getattr(self, first)
                if attribute == last:
                    person.surname = getattr(self, last)
            persons.append(person)
        # We use list comprehension to get the numbered persons to
        # ease code maintentenance and easily support a larger range if necessary
        persons.extend(
            self.__get_numbered_persons__(
                attributes=attributes,
                role=EnglishWikipediaTemplatePersonRole.AUTHOR,
                search_string=str(role.value),
            )
        )
        # console.print(f"{role.name}s: {persons}")
        return persons

    def __parse_persons__(self) -> None:
        """Parse all person related data into Person objects"""
        # find all the attributes but exclude the properties as they lead to weird errors
        properties = ["has_hash", "isodate", "template_url", "wikibase_url"]
        attributes = [
            a
            for a in dir(self)
            if not a.startswith("_")
            and a not in properties
            and not callable(getattr(self, a))
            and getattr(self, a) is not None
        ]
        self.authors_list = self.__parse_known_role_persons__(
            attributes=attributes, role=EnglishWikipediaTemplatePersonRole.AUTHOR
        )
        self.editors_list = self.__parse_known_role_persons__(
            attributes=attributes, role=EnglishWikipediaTemplatePersonRole.EDITOR
        )
        self.hosts_list = self.__parse_known_role_persons__(
            attributes=attributes, role=EnglishWikipediaTemplatePersonRole.HOST
        )
        self.interviewers_list = self.__parse_known_role_persons__(
            attributes=attributes, role=EnglishWikipediaTemplatePersonRole.INTERVIEWER
        )
        self.persons_without_role = self.__parse_roleless_persons__(
            attributes=attributes
        )
        self.translators_list = self.__parse_known_role_persons__(
            attributes=attributes, role=EnglishWikipediaTemplatePersonRole.TRANSLATOR
        )

    @validate_arguments
    def __parse_roleless_persons__(self, attributes: List[str]) -> List[Person]:
        persons = []
        # first last
        unnumbered_first_last = [
            attribute
            for attribute in attributes
            if self.__find_number__(attribute) is None
            and (attribute == "first" or attribute == "last")
        ]
        logger.debug(f"{len(unnumbered_first_last)} unnumbered first lasts found.")
        if len(unnumbered_first_last) > 0:
            person = Person(
                role=EnglishWikipediaTemplatePersonRole.UNKNOWN,
            )
            for attribute in unnumbered_first_last:
                # print(attribute, getattr(self, attribute))
                if attribute == "first":
                    person.given = self.first
                if attribute == "last":
                    person.surname = self.last
            # console.print(person)
            persons.append(person)
            # exit()
        # We use list comprehension to get the numbered persons to
        # ease code maintentenance and easily support a larger range if necessary
        persons.extend(self.__get_numbered_persons__(attributes=attributes))
        return persons

    def __parse_url__(self, url: str = "") -> str:
        # Guard against URLs like "[[:sq:Shkrime për historinë e Shqipërisë|Shkrime për historinë e Shqipërisë]]"
        parsed_url = urlparse(url)
        if parsed_url.scheme:
            url = parsed_url.geturl()
            logger.info(f"Found scheme in {url}")
            return url
        else:
            if self.__has_template_data__(string=url):
                logger.info(f"Found template data in url: {url}")
                return self.__get_url_from_template__(url=url)
            else:
                logger.warning(
                    f"Skipped the URL '{self.url}' because of missing URL scheme"
                )
                return ""

    def __parse_urls__(self) -> None:
        """This function looks for Google Books references and
        parse the URLs to avoid complaints from Wikibase"""
        logger.debug("__parse_urls__: Running")
        if self.url:
            self.url = self.__parse_url__(url=self.url)
        if self.archive_url:
            self.archive_url = self.__parse_url__(url=self.archive_url)
        if self.lay_url:
            self.lay_url = self.__parse_url__(url=self.lay_url)
        if self.chapter_url:
            self.chapter_url = self.__parse_url__(url=self.chapter_url)
        if self.conference_url:
            self.conference_url = self.__parse_url__(url=self.conference_url)
        if self.transcripturl:
            self.transcripturl = self.__parse_url__(url=self.transcripturl)

    @validator(
        "access_date",
        "archive_date",
        "date",
        "doi_broken_date",
        "orig_date",
        "orig_year",
        "pmc_embargo_date",
        "publication_date",
        "time",
        "year",
        pre=True,
    )
    def __validate_time__(cls, v) -> Optional[datetime]:  # type: ignore # mypy: ignore
        """Pydantic validator
        see https://stackoverflow.com/questions/66472255/"""
        date = None
        # Support "2013-01-01"
        try:
            date = datetime.strptime(v, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        # Support "May 9, 2013"
        try:
            date = datetime.strptime(v, "%B %d, %Y").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        # Support "Jul 9, 2013"
        try:
            date = datetime.strptime(v, "%b %d, %Y").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        # Support "May 25, 2012a"
        try:
            date = datetime.strptime(v[:-1], "%b %d, %Y").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        # Support "1 September 2003"
        try:
            date = datetime.strptime(v, "%d %B %Y").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        # Support "26 Dec 1996"
        try:
            date = datetime.strptime(v, "%d %b %Y").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        # Support "September 2003"
        try:
            date = datetime.strptime(v, "%B %Y").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        # Support "Sep 2003"
        try:
            date = datetime.strptime(v, "%b %Y").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        # Support "2003"
        try:
            date = datetime.strptime(v, "%Y").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        if date is None:
            # raise TimeParseException(f"date format '{v}' not supported yet")
            logger.warning(f"date format '{v}' not supported yet")
        return date

    @validate_arguments
    def __upload_reference_to_wikibase__(
        self, wikipedia_article=None
    ) -> WikibaseReturn:
        """This method tries to upload the reference to Wikibase
        and returns a WikibaseReturn."""
        logger.debug("__upload_reference_to_wikicitations__: Running")
        if self.wikibase_crud_create is None:
            self.__setup_wikibase_crud_create__()
        if self.wikibase_crud_create:
            return_ = self.wikibase_crud_create.prepare_and_upload_reference_item(
                page_reference=self, wikipedia_article=wikipedia_article
            )
            if isinstance(return_, WikibaseReturn):
                return return_
            else:
                raise ValueError(f"we did not get a WikibaseReturn back")

        else:
            raise ValueError("self.wikibase_crud_create was None")

    @validate_arguments
    def get_wcdqid_from_cache(self) -> None:
        if self.cache is None:
            self.__setup_cache__()
        if self.cache is not None:
            self.return_: CacheReturn = self.cache.check_reference_and_get_wikibase_qid(
                reference=self
            )
            logger.debug(f"result from the cache:{self.return_.item_qid}")
        else:
            raise ValueError("self.cache was None")

    @validate_arguments
    def __insert_reference_in_cache__(self, wcdqid: str):
        """Insert reference in the cache"""
        logger.debug("__insert_in_cache__: Running")
        if self.cache is None:
            self.__setup_cache__()
        if self.cache is not None:
            self.cache.add_reference(reference=self, wcdqid=wcdqid)
        else:
            raise ValueError("self.cache was None")
        logger.info("Reference inserted into the hash database")

    @validate_arguments
    def upload_reference_and_insert_in_the_cache_if_enabled(self) -> None:
        """Upload the reference and insert into the cache if enabled. Always add return_"""
        logger.debug("__upload_reference_and_insert_in_the_cache_if_enabled__: Running")
        return_ = self.__upload_reference_to_wikibase__()
        if not return_ or not self.md5hash:
            raise MissingInformationError("hash or WCDQID was None")
        self.__insert_reference_in_cache__(wcdqid=return_.item_qid)
        self.return_ = return_

    def finish_parsing_and_generate_hash(self, testing: bool = False) -> None:
        """Parse the rest of the information and generate a hash"""
        # We parse the first parameter before isbn
        from src.models.update_delay import UpdateDelay

        update_delay = UpdateDelay(object_=self)
        if update_delay.time_to_update or testing is True:
            self.__parse_first_parameter__()
            self.__parse_urls__()
            self.__parse_isbn__()
            # First Level Domain detection is needed for the detection methods
            self.__extract_first_level_domain__()
            self.__detect_archive_urls__()
            self.__detect_internet_archive_id__()
            # self.__detect_google_books_id__()
            self.__parse_persons__()
            self.__merge_date_into_publication_date__()
            self.__merge_lang_into_language__()
            self.__merge_place_into_location__()
            self.__clean_wiki_markup_from_strings__()
            # We generate the hash last because the parsing needs to be done first
            self.__generate_hashes__()

    def insert_last_update_timestamp(self):
        from src.models.cache import Cache
        from src.models.hash_ import Hash_

        hash_ = Hash_(
            wikibase=self.wikibase,
            language_code=self.language_code,
            title=self.title,
            wikimedia_site=self.wikimedia_site,
        )
        cache = Cache()
        cache.connect()
        cache.set_title_or_wdqid_last_updated(key=hash_.__entity_updated_hash_key__())

    @staticmethod
    def __has_template_data__(string: str) -> bool:
        """This is a very simple test for two opening curly brackets"""
        if "{{" in string:
            return True
        else:
            return False

    def __get_url_from_template__(self, url: str) -> str:
        if "google books" in url.lower():
            logger.info("Found Google books template")
            return self.__get_url_from_google_books_template__(url=url)
        else:
            logger.warning(f"Parsing the template data in {url} is not supported yet")
            return ""

    @staticmethod
    def __get_url_from_google_books_template__(url: str) -> str:
        """Parse the Google Books template that sometimes appear in a url
        and return the generated url"""
        logger.debug("__get_url_from_google_books_template__: Running")
        template_tuples = extract_templates_and_params(url, True)
        if template_tuples:
            for _template_name, content in template_tuples:
                google_books: GoogleBooks = GoogleBooksSchema().load(content)
                google_books.finish_parsing()
                # We only care about the first
                return str(google_books.url)
            logger.warning(f"Parsing the google books template data in {url} failed")
            return ""
        else:
            logger.warning(f"Parsing the google books template data in {url} failed")
            return ""
