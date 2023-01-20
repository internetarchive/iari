import logging
from urllib.parse import urlparse

import requests
from dns.resolver import NXDOMAIN, LifetimeTimeout, NoNameservers, resolve
from pydantic import BaseModel
from requests import ConnectTimeout, ReadTimeout
from tld import get_fld
from tld.exceptions import TldBadUrl
from urllib3.connectionpool import MaxRetryError, SSLError
from urllib3.exceptions import NewConnectionError

from src.models.exceptions import ResolveError

logger = logging.getLogger(__name__)


class WikipediaUrl(BaseModel):
    """This models a URL
    It uses BaseModel to avoid the cache
    attribute so we can output it via the API easily"""

    soft404_probability: float = 0.0
    url: str
    checked: bool = False
    status_code: int = 0
    first_level_domain: str = ""
    timeout_or_retry_error: bool = False
    no_dns_record: bool = False
    malformed_url: bool = False
    ssl_error: bool = False

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

    def __lt__(self, other):
        return self.url < other.url

    @property
    def check_soft404(self):
        raise NotImplementedError()

    @property
    def __netloc__(self) -> str:
        parsed_url = urlparse(self.url)
        netloc = parsed_url.netloc
        if not netloc:
            self.malformed_url = True
            # try fixing urls like these: httproe.ru/pdfs/pdf_1914.pdf
            parsed_url = urlparse("http://" + self.url)
            netloc = parsed_url.netloc
            if not netloc:
                return ""
        return netloc

    @property
    def __dns_record_found__(self) -> bool:
        # if domain name is available
        netloc = self.__netloc__
        if netloc:
            print(f"Trying to resolve {netloc}")
            try:
                answers = resolve(netloc)
                if answers:
                    return True
                else:
                    raise ResolveError("no answers")
            except NXDOMAIN:
                self.no_dns_record = True
                return False
            except (LifetimeTimeout, NoNameservers):
                self.timeout_or_retry_error = True
                return False
        else:
            self.malformed_url = True
            return False

    def __fix_malformed_urls__(self):
        self.__fix_malformed_httpwww__()
        self.__fix_malformed_httpswww__()

    def __fix_malformed_httpwww__(self):
        if self.url.startswith("httpwww"):
            self.malformed_url = True
            self.url = self.url.replace("httpwww", "http://www")

    def __fix_malformed_httpswww__(self):
        if self.url.startswith("httpswww"):
            self.malformed_url = True
            self.url = self.url.replace("httpswww", "https://www")

    def check_with_https_verify(self):
        try:
            # https://stackoverflow.com/questions/66710047/
            # python-requests-library-get-the-status-code-without-downloading-the-target
            r = requests.head(self.url, timeout=2, verify=True)
            self.status_code = r.status_code
            logger.debug(self.url + "\tStatus: " + str(r.status_code))
            # if r.status_code == 200:
            #     self.check_soft404
        # https://stackoverflow.com/questions/6470428/catch-multiple-exceptions-in-one-line-except-block
        except (ReadTimeout, ConnectTimeout, MaxRetryError, NewConnectionError):
            self.timeout_or_retry_error = True
        except (SSLError, requests.exceptions.SSLError):
            self.ssl_error = True

    def check_without_https_verify(self):
        # https://jcutrer.com/python/requests-ignore-invalid-ssl-certificates
        try:
            # https://stackoverflow.com/questions/66710047/
            # python-requests-library-get-the-status-code-without-downloading-the-target
            r = requests.head(self.url, timeout=1, verify=False)
            self.status_code = r.status_code
            logger.debug(self.url + "\tStatus: " + str(r.status_code))
            # if r.status_code == 200:
            #     self.check_soft404
        # https://stackoverflow.com/questions/6470428/catch-multiple-exceptions-in-one-line-except-block
        except (ReadTimeout, ConnectTimeout, MaxRetryError, NewConnectionError):
            self.timeout_or_retry_error = True

    def fix_and_check(self):
        logger.debug("fix_and_check: running")
        self.__fix_malformed_urls__()
        print(f"Trying to check: {self.url}")
        if self.__dns_record_found__:
            self.check_with_https_verify()
            if self.ssl_error:
                self.check_without_https_verify()
        logger.debug("setting checked to true")
        self.checked = True

    def is_google_books_url(self):
        return bool("//books.google." in self.url)

    def is_wayback_machine_url(self):
        return bool("//web.archive.org" in self.url)

    def is_ia_details_url(self):
        """Checks for Internet Archive details url"""
        return bool("//archive.org/details" in self.url)

    def get_first_level_domain(self):
        logger.debug("__get_first_level_domain__: Running")
        try:
            logger.debug(f"Trying to get FLD from {self.url}")
            fld = get_fld(self.url)
            if fld:
                logger.debug(f"Found FLD: {fld}")
                self.first_level_domain = fld
        except TldBadUrl:
            """The library does not support Wayback Machine URLs"""
            if self.is_wayback_machine_url():
                return "archive.org"
            else:
                message = f"Bad url {self.url} encountered"
                logger.warning(message)
                # self.__log_to_file__(
                #     message=str(message), file_name="url_exceptions.log"
                # )
                # return None
