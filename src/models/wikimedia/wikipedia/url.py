import logging
import re
from ipaddress import ip_address
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import validators  # type: ignore
from pydantic import BaseModel
from tld import get_fld
from tld.exceptions import TldBadUrl, TldDomainNotFound

from src.models.wikimedia.wikipedia.enums import MalformedUrlError

logger = logging.getLogger(__name__)


class WikipediaUrl(BaseModel):
    """This models a URL in Wikipedia
    It uses BaseModel to avoid the cache
    attribute, so we can output it via the API easily

    We do not perform any checking or lookup here that requires HTTP requests.
    We only check based on the URL itself.
    """

    url: str
    scheme: str = ""  # url scheme e.g. http
    first_level_domain: str = ""
    netloc: str = ""  # network location e.g. google.com
    fld_is_ip: bool = False  # first level domain is an IP address
    tld: str = ""  # top level domain
    malformed_url: bool = False
    malformed_url_details: Optional[MalformedUrlError] = None
    archived_url: str = ""
    wayback_machine_timestamp: str = ""

    @property
    def __is_wayback_machine_url__(self):
        logger.debug("is_wayback_machine_url: running")
        return bool("//web.archive.org" in self.url)

    @property
    def get_dict(self) -> Dict[str, Any]:
        url = self.dict()
        if self.malformed_url_details:
            url.update({"malformed_url_details": self.malformed_url_details.value})
        return url

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

    def __lt__(self, other):
        return self.url < other.url

    def __parse_extract_and_validate__(self) -> None:
        logger.debug("__parse_extract_and_validate__: running")
        if self.__is_wayback_machine_url__:
            self.__parse_wayback_machine_url__()
        self.__parse_and_extract_url__()
        self.__extract_tld__()
        self.__check_scheme__()

    def __extract_first_level_domain__(self) -> None:
        from src import app

        app.logger.debug("__extract_first_level_domain__: Running")
        try:
            self.__get_fld__()
        except (TldBadUrl, TldDomainNotFound):
            try:
                ip = ip_address(self.netloc)
                logger.debug(f"found IP: {ip}")
                self.first_level_domain = str(ip)
                self.fld_is_ip = True
            except ValueError:
                # Not a valid IPv4 or IPv6 address.
                message = f"Could not extract fld from {self.url}"
                logger.warning(message)
                # self.__log_to_file__(
                #     message=str(message), file_name="url_exceptions.log"
                # )

    def __check_scheme__(self):
        """Check for one of 4 know schemes that Wikipedia accepts"""
        if not self.scheme:
            logger.debug(f"Could not find urlscheme in {self.url}")
            self.malformed_url = True
            self.malformed_url_details = MalformedUrlError.MISSING_SCHEME
        else:
            if self.scheme not in ["http", "https", "ftp", "sftp"]:
                logger.debug(f"Unrecognized scheme: {self.scheme}")
                self.malformed_url = True
                self.malformed_url_details = MalformedUrlError.UNRECOGNIZED_SCHEME
            else:
                logger.debug(f"Found valid urlscheme: {self.scheme}")

    def __extract_tld__(self):
        if not self.netloc:
            logger.warning("Could not extract tld because self.netloc was empty")
        else:
            self.tld = self.netloc.split(".")[-1]
            logger.debug(f"tld found: {self.tld}")

    def __parse_and_extract_url__(self):
        """
        Parse and extract netloc and scheme

        self.archived_url is set if url has been determined to be a wayback machine archive
        """
        parsed_url = (
            urlparse(self.archived_url) if self.archived_url else urlparse(self.url)
        )
        logger.debug(f"parsed_url: {parsed_url}")
        self.netloc = parsed_url.netloc
        if not self.netloc:
            logger.warning(
                f"Could not get netloc from {self.url} so we consider it malformed"
            )
            self.malformed_url = True
            self.malformed_url_details = MalformedUrlError.NO_NETLOC_FOUND
        self.scheme = parsed_url.scheme
        # We ignore the other parts for now

    def __parse_wayback_machine_url__(self):
        """Parse Wayback Machine URLs and extract both timestamp and archived url
        Is there no official library to do this?
        Example urls:
        https://web.archive.org/web/20220000000000*/https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2016/11/sou-20167?test=2
        https://web.archive.org/web/20141031094104/http://collections.rmg.co.uk/collections/objects/13275.html
        """
        logger.debug("__parse_wayback_machine_url__: running")
        # Extract the remaining portion of the URL after the timestamp
        result = re.search(r"https?://web\.archive\.org/web/([\d*]+)/(.*)", self.url)
        if result:
            self.wayback_machine_timestamp = result.group(1)
            self.archived_url = result.group(2)
        if not self.archived_url:
            message = f"Could not parse the archived url from '{self.url}'"
            logger.warning(message)
            # self.__log_to_file__(
            #     message=str(message), file_name="url_exceptions.log"
            # )

    def __get_fld__(self):
        logger.debug("__get_fld__: running")
        if self.archived_url:
            logger.debug(f"Trying to get FLD from {self.archived_url}")
            fld = get_fld(self.archived_url)
        else:
            logger.debug(f"Trying to get FLD from {self.url}")
            fld = get_fld(self.url)
        logger.debug(f"Found FLD: {fld}")
        self.first_level_domain = fld

    def extract(self):
        from src import app

        app.logger.debug("extract: running")
        self.__parse_extract_and_validate__()
        self.__extract_first_level_domain__()
