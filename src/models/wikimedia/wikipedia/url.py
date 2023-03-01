import logging
from ipaddress import ip_address
from urllib.parse import urlparse

from pydantic import BaseModel
from tld import get_fld
from tld.exceptions import TldBadUrl, TldDomainNotFound

logger = logging.getLogger(__name__)


class WikipediaUrl(BaseModel):
    """This models a URL in Wikipedia
    It uses BaseModel to avoid the cache
    attribute so we can output it via the API easily

    We do not perform any checking or lookup here that requires HTTP requests.
    We only check based on the URL itself.
    """

    parsing_done: bool = False
    first_level_domain: str = ""
    first_level_domain_done: bool = False
    fld_is_ip: bool = False  # first level domain is an IP adress
    url: str
    fixed_url: str = ""
    scheme: str = ""  # url scheme e.g. http
    netloc: str = ""  # network location e.g. google.com
    tld: str = ""  # top level domain
    unrecognized_scheme: bool = False
    unrecognized_tld: bool = False
    added_http_scheme_worked: bool = False

    @property
    def __get_url__(self) -> str:
        """Helper method to get the fixed url and fall back to the original url"""
        if self.fixed_url:
            return self.fixed_url
        else:
            return self.url

    def __hash__(self):
        return hash(self.__get_url__)

    def __eq__(self, other):
        return self.__get_url__ == other.url

    def __lt__(self, other):
        return self.__get_url__ < other.url

    def __parse_extract_and_validate__(self) -> None:
        if not self.parsing_done:
            logger.debug("__parse_and_validate__: running")
            self.__parse_and_extract_url__()
            self.__extract_tld__()
            self.__check_tld__()
            self.__check_scheme__()
            self.__check_and_fix_netloc__()
            self.parsing_done = True

    def extract(self):
        logger.debug("fix_and_extract_and_check: running")
        self.__parse_extract_and_validate__()
        self.extract_first_level_domain()

    # TODO rewrite to expose these in the API also
    def is_google_books_url(self):
        return bool("//books.google." in self.__get_url__)

    def is_wayback_machine_url(self):

        return bool("//web.archive.org" in self.__get_url__)

    def is_ia_details_url(self):
        """Checks for Internet Archive details url"""

        return bool("//archive.org/details" in self.__get_url__)

    def extract_first_level_domain(self) -> None:
        logger.debug("__get_first_level_domain__: Running")
        try:
            logger.debug(f"Trying to get FLD from {self.__get_url__}")
            fld = get_fld(self.__get_url__)
            if fld:
                logger.debug(f"Found FLD: {fld}")
                self.first_level_domain = fld
            self.first_level_domain_done = True
        except (TldBadUrl, TldDomainNotFound):
            """The library does not support Wayback Machine URLs"""
            if self.is_wayback_machine_url():
                self.first_level_domain = "archive.org"
            else:
                try:
                    ip = ip_address(self.netloc)
                    logger.debug(f"found IP: {ip}")
                    self.first_level_domain = str(ip)
                    self.fld_is_ip = True
                except ValueError:
                    # Not a valid IPv4 or IPv6 address.
                    message = f"Could not extract fld from {self.__get_url__}"
                    logger.warning(message)
                    # self.__log_to_file__(
                    #     message=str(message), file_name="url_exceptions.log"
                    # )
            self.first_level_domain_done = True

    def __check_tld__(self):
        """We only check the length for now"""
        logger.debug("__check_tld__: running")
        if not self.netloc:
            logger.warning("netloc was empty")
        else:
            if len(self.tld) not in [2, 6]:
                logger.warning(f"TLD '{self.tld}' in {self.__get_url__} not recognized")
                self.unrecognized_tld = True
                self.malformed_url = True
            else:
                logger.debug(
                    f"TLD '{self.tld}' in {self.__get_url__} was correct length"
                )

    def __check_scheme__(self):
        """Check for one of 4 know schemes that Wikipedia accepts"""
        if not self.scheme:
            logger.debug(f"Could not find urlscheme in {self.__get_url__}")
            self.scheme_missing = True
        else:
            if self.scheme not in ["http", "https", "ftp", "sftp"]:
                logger.debug(f"Unrecognized scheme: {self.scheme}")
                self.malformed_url = True
                self.unrecognized_scheme = True
            else:
                logger.debug(f"Found valid urlscheme: {self.scheme}")

    def __check_and_fix_netloc__(self):
        """Check if the netloc is valid"""
        if not self.netloc:
            logger.warning(
                f"Could not get netloc from {self.__get_url__} so we consider it malformed"
            )
            self.malformed_url = True
            # try fixing urls like these: httproe.ru/pdfs/pdf_1914.pdf
            parsed_url = urlparse("http://" + self.__get_url__)
            netloc = parsed_url.netloc
            if not netloc:
                self.no_netloc = True
                return ""
            else:
                logger.info(
                    f"Adding 'http://' to {self.__get_url__} made it possible to extract netloc"
                )
                self.netloc = netloc
                self.fixed_url = parsed_url.geturl()
                self.added_http_scheme_worked = True
        else:
            logger.info(f"netloc {self.netloc} seems good")

    def __extract_tld__(self):
        if not self.netloc:
            logger.warning(f"Could not extract tld because self.netloc was empty")
        else:
            self.tld = self.netloc.split(".")[-1]
            logger.debug(f"tld found: {self.tld}")

    def __parse_and_extract_url__(self):
        """Parse and extract netloc and scheme"""
        parsed_url = urlparse(self.__get_url__)
        # console.print(parsed_url)
        self.netloc = parsed_url.netloc
        self.scheme = parsed_url.scheme
        # We ignore the other parts for now
