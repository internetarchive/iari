import logging
from ipaddress import ip_address
from urllib.parse import urlparse

import requests
from dns.resolver import NXDOMAIN, LifetimeTimeout, NoAnswer, NoNameservers, resolve
from pydantic import BaseModel
from requests.exceptions import (
    ConnectionError,
    ConnectTimeout,
    HTTPError,
    InvalidHeader,
    InvalidProxyURL,
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    ProxyError,
    ReadTimeout,
    RequestException,
    RetryError,
    SSLError,
    Timeout,
)
from tld import get_fld
from tld.exceptions import TldBadUrl, TldDomainNotFound

from src.models.exceptions import ResolveError

logger = logging.getLogger(__name__)
timeout = 2


class WikipediaUrl(BaseModel):
    """This models a URL
    It uses BaseModel to avoid the cache
    attribute so we can output it via the API easily"""

    checked: bool = False
    error: bool = False
    first_level_domain: str = ""
    first_level_domain_done: bool = False
    fld_is_ip: bool = False
    malformed_url: bool = False
    no_dns_record: bool = False
    # soft404_probability: float = 0.0
    status_code: int = 0
    url: str

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

    def __lt__(self, other):
        return self.url < other.url

    @property
    def __check_soft404__(self):
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
        logger.debug("__dns_record_found__: running")
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
            except (LifetimeTimeout, NoNameservers, NoAnswer):
                self.error = True
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

    def __check_with_https_verify__(self):
        logger.debug("__check_with_https_verify__: running")
        try:
            # https://stackoverflow.com/questions/66710047/
            # python-requests-library-get-the-status-code-without-downloading-the-target
            r = requests.head(self.url, timeout=timeout, verify=True)
            self.status_code = r.status_code
            logger.debug(self.url + "\tStatus: " + str(r.status_code))
            # if r.status_code == 200:
            #     self.check_soft404
        # https://stackoverflow.com/questions/6470428/catch-multiple-exceptions-in-one-line-except-block
        except (
            ReadTimeout,
            ConnectTimeout,
            RetryError,
            InvalidHeader,
            Timeout,
            ConnectionError,
            RequestException,
            HTTPError,
            ProxyError,
        ) as e:
            logger.debug(f"got exception: {e}")
            self.error = True
        except (MissingSchema, InvalidSchema, InvalidURL, InvalidProxyURL) as e:
            logger.debug(f"got exception: {e}")
            self.malformed_url = True
        except SSLError:
            self.ssl_error = True

    def __check_without_https_verify__(self):
        # https://jcutrer.com/python/requests-ignore-invalid-ssl-certificates
        logger.debug("__check_without_https_verify__: running")
        try:
            # https://stackoverflow.com/questions/66710047/
            # python-requests-library-get-the-status-code-without-downloading-the-target
            r = requests.head(self.url, timeout=timeout, verify=False)
            self.status_code = r.status_code
            logger.debug(self.url + "\tStatus: " + str(r.status_code))
            # if r.status_code == 200:
            #     self.check_soft404
        # https://stackoverflow.com/questions/6470428/catch-multiple-exceptions-in-one-line-except-block
        except (
            ReadTimeout,
            ConnectTimeout,
            RetryError,
            InvalidHeader,
            Timeout,
            ConnectionError,
            RequestException,
            HTTPError,
            ProxyError,
        ) as e:
            logger.debug(f"got exception: {e}")
            self.error = True
        except (MissingSchema, InvalidSchema, InvalidURL, InvalidProxyURL) as e:
            logger.debug(f"got exception: {e}")
            self.malformed_url = True

    def fix_and_extract_and_check(self):
        logger.debug("fix_and_extract_and_check: running")
        self.__fix_malformed_urls__()
        self.extract_first_level_domain()
        print(f"Trying to check: {self.url}")
        if self.__dns_record_found__:
            self.__check_with_https_verify__()
            if self.error:
                self.__check_without_https_verify__()
        logger.debug("setting checked to true")
        self.checked = True

    def is_google_books_url(self):
        return bool("//books.google." in self.url)

    def is_wayback_machine_url(self):
        return bool("//web.archive.org" in self.url)

    def is_ia_details_url(self):
        """Checks for Internet Archive details url"""
        return bool("//archive.org/details" in self.url)

    def extract_first_level_domain(self) -> None:
        logger.debug("__get_first_level_domain__: Running")
        try:
            logger.debug(f"Trying to get FLD from {self.url}")
            fld = get_fld(self.url)
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
                    ip = ip_address(self.__netloc__)
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
            self.first_level_domain_done = True
