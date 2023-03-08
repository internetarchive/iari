import logging
from typing import Any, Dict

import requests
from dns.resolver import NXDOMAIN, LifetimeTimeout, NoAnswer, NoNameservers, resolve
from requests import (
    ConnectionError,
    ConnectTimeout,
    HTTPError,
    ReadTimeout,
    RequestException,
    Timeout,
)
from requests.exceptions import (
    InvalidHeader,
    InvalidProxyURL,
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    ProxyError,
    RetryError,
    SSLError,
)

from src import console
from src.models.exceptions import ResolveError
from src.models.wikimedia.wikipedia.url import WikipediaUrl

logger = logging.getLogger(__name__)


class Url(WikipediaUrl):
    """
    This handles checking a URL

    Our patrons want to know if this URL is likely to lead to the content that is referenced.

    We define a malformed URL as any URL that the reader cannot easily
    click and successfully get the contents of in a normal web browser session
    """

    request_error: bool = False
    malformed_url: bool = False
    dns_record_found: bool = False
    dns_no_answer: bool = False
    request_url_error: bool = False
    dns_error: bool = False
    # soft404_probability: float = 0.0  # not implemented yet
    status_code: int = 0
    timeout: int = 2

    # @property
    # def __check_soft404__(self):
    #     raise NotImplementedError()

    def check(self):
        self.extract()
        self.__fix_malformed_urls__()
        self.__check_url__()

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

    def __check_with_https_verify__(self):
        logger.debug("__check_with_https_verify__: running")

        try:
            # https://stackoverflow.com/questions/66710047/
            # python-requests-library-get-the-status-code-without-downloading-the-target
            r = requests.head(self.__get_url__, timeout=self.timeout, verify=True)
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
            r = requests.head(self.__get_url__, timeout=self.timeout, verify=False)
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

    def __check_url__(self):
        print(f"Trying to check: {self.__get_url__}")
        self.__get_dns_record__()
        self.__check_with_https_verify__()
        if self.request_error:
            self.__check_without_https_verify__()

    def get_dict(self) -> Dict[str, Any]:
        cleaned_dictionary = self.dict(
            exclude={"parsing_done", "first_level_domain_done"}
        )
        console.print(cleaned_dictionary)
        return cleaned_dictionary
