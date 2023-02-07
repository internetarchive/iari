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
    attribute so we can output it via the API easily

    We define a malformed URL as any URL that the reader cannot easily
    click and successfully get the contents of in a normal web browser session"""

    checked: bool = False
    request_error: bool = False
    first_level_domain: str = ""
    first_level_domain_done: bool = False
    fld_is_ip: bool = False
    malformed_url: bool = False
    dns_record_found: bool = False
    scheme_missing: bool = False
    added_http_scheme_worked: bool = False
    dns_no_answer: bool = False
    no_netloc: bool = False
    request_url_error: bool = False
    unrecognized_scheme: bool = False
    unrecognized_tld: bool = False
    parsing_done: bool = False
    dns_error: bool = False
    # soft404_probability: float = 0.0
    status_code: int = 0
    url: str
    fixed_url: str = ""
    scheme: str = ""
    netloc: str = ""
    tld: str = ""

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

    @property
    def __check_soft404__(self):
        raise NotImplementedError()

    def __parse_extract_and_validate__(self) -> None:
        if not self.parsing_done:
            logger.debug("__parse_and_validate__: running")
            self.__parse_and_extract_url__()
            self.__extract_tld__()
            self.__check_tld__()
            self.__check_scheme__()
            self.__check_and_fix_netloc__()
            self.parsing_done = True

    def __get_dns_record__(self) -> None:
        logger.debug("__get_dns_record__: running")
        # if domain name is available
        if self.netloc:
            logger.info(f"Trying to resolve {self.netloc}")
            try:
                answers = resolve(self.netloc)
                if answers:
                    self.dns_record_found = True
                else:
                    raise ResolveError("no answers")
            except NXDOMAIN:
                pass
            except (
                LifetimeTimeout,
                NoNameservers,
            ):
                self.dns_error = True
            except NoAnswer:
                self.dns_no_answer = True
        else:
            logger.warning("Could not get DNS because netloc was empty")

    def __fix_malformed_urls__(self):
        """This fixes common errors found in the urls"""
        self.__fix_malformed_httpwww__()
        self.__fix_malformed_httpswww__()

    def __fix_malformed_httpwww__(self):
        """This fixes a common error found in Wikipedia urls"""
        if self.__get_url__.startswith("httpwww"):
            self.malformed_url = True
            self.fixed_url = self.__get_url__.replace("httpwww", "http://www")

    def __fix_malformed_httpswww__(self):
        """This fixes a common error found in Wikipedia urls"""
        if self.__get_url__.startswith("httpswww"):
            self.malformed_url = True
            self.fixed_url = self.__get_url__.replace("httpswww", "https://www")

    def __check_with_https_verify__(self):
        logger.debug("__check_with_https_verify__: running")

        try:
            # https://stackoverflow.com/questions/66710047/
            # python-requests-library-get-the-status-code-without-downloading-the-target
            r = requests.head(self.__get_url__, timeout=timeout, verify=True)
            self.status_code = r.status_code
            logger.debug(self.__get_url__ + "\tStatus: " + str(r.status_code))
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
            self.request_error = True
        except (MissingSchema, InvalidSchema, InvalidURL, InvalidProxyURL) as e:
            logger.debug(f"got exception: {e}")
            self.request_url_error = True
            self.malformed_url = True
        except SSLError:
            self.ssl_error = True

    def __check_without_https_verify__(self):
        # https://jcutrer.com/python/requests-ignore-invalid-ssl-certificates
        logger.debug("__check_without_https_verify__: running")

        try:
            # https://stackoverflow.com/questions/66710047/
            # python-requests-library-get-the-status-code-without-downloading-the-target
            r = requests.head(self.__get_url__, timeout=timeout, verify=False)
            self.status_code = r.status_code
            logger.debug(self.__get_url__ + "\tStatus: " + str(r.status_code))
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
            self.request_error = True
        except (MissingSchema, InvalidSchema, InvalidURL, InvalidProxyURL) as e:
            logger.debug(f"got exception: {e}")
            self.malformed_url = True

    def fix_and_extract_and_check(self):
        logger.debug("fix_and_extract_and_check: running")
        self.__fix_malformed_urls__()
        self.__parse_extract_and_validate__()
        self.extract_first_level_domain()
        self.__check_url__()

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
            if len(self.tld) not in [2, 3]:
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

    def __check_url__(self):
        print(f"Trying to check: {self.__get_url__}")
        self.__get_dns_record__()
        self.__check_with_https_verify__()
        if self.request_error:
            self.__check_without_https_verify__()
        # logger.debug("setting checked to true")
        self.checked = True
