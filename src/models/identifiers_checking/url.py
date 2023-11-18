import logging
import os
import urllib.parse
from typing import Any, Dict, Optional

import requests
from dns.name import EmptyLabel
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
from requests.models import LocationParseError

from src.models.api.handlers import BaseHandler
from src.models.exceptions import ResolveError
from src.models.wikimedia.wikipedia.url import WikipediaUrl

logger = logging.getLogger(__name__)


class Url(WikipediaUrl):
    """
    This handles checking a URL

    Our patrons want to know if this URL is likely to lead to the content that is referenced.

    We define a malformed URL as any URL that the reader cannot easily
    click and successfully get the contents of in a normal web browser session

    We send spoofing headers by default to avoid 4xx as much as possible
    and do not offer turning them off for now.
    """

    # iari test - deprecated, for now (2023.11.08)
    status_code: int = 0

    # iabot status
    testdeadlink_status_code: int = 0
    testdeadlink_error_details: str = ""

    # IABot WBM status
    searchurldata_results: Optional[Dict] = None

    text: str = ""
    response_headers: Optional[Dict] = None

    detected_language: str = ""
    detected_language_error: bool = False
    detected_language_error_details: str = ""

    request_error: bool = False
    request_error_details: str = ""
    timeout: int = 2

    dns_record_found: bool = False
    dns_no_answer: bool = False
    dns_error: bool = False
    dns_error_details: str = ""

    # soft404_probability: float = 0.0  # not implemented yet

    # @property
    # def __check_soft404__(self):
    #     raise NotImplementedError()

    def check(self):
        if self.url:
            self.extract()
            # self.__check_url__()  # omit native IARI checking for now - just ise IABot's
            self.__check_url_with_testdeadlink_api__()
            self.__check_url_with_searchurldata_api__()
            self.__detect_language__()

    def __get_dns_record__(self) -> None:
        from src import app

        app.logger.debug("__get_dns_record__: running")

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
            except (LifetimeTimeout, NoNameservers, EmptyLabel) as e:
                self.dns_error = True
                self.dns_error_details = str(e)
            except NoAnswer:
                self.dns_no_answer = True
        else:
            logger.warning("Could not get DNS because netloc was empty")

    def __check_with_https_verify__(self):
        from src import app

        app.logger.debug("__check_with_https_verify__: running")

        try:
            # https://stackoverflow.com/questions/66710047/
            # python-requests-library-get-the-status-code-without-downloading-the-target
            r = requests.get(
                self.url,
                timeout=self.timeout,
                verify=True,
                headers=self.__spoofing_headers__,
                allow_redirects=True,
            )
            self.status_code = r.status_code
            logger.debug(self.url + "\tStatus: " + str(r.status_code))
            self.response_headers = dict(r.headers)
            if r.status_code == 200:
                self.text = r.text
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
            LocationParseError,
        ) as e:
            logger.debug(f"got exception: {e}")
            self.request_error = True
            self.request_error_details = str(e)
        except (MissingSchema, InvalidSchema, InvalidURL, InvalidProxyURL) as e:
            logger.debug(f"got exception: {e}")
            self.malformed_url = True
            self.request_error = True
            self.request_error_details = str(e)
        except SSLError:
            self.request_error = True
            self.ssl_error = True

    def __check_without_https_verify__(self):
        from src import app

        # https://jcutrer.com/python/requests-ignore-invalid-ssl-certificates
        app.logger.debug("__check_without_https_verify__: running")

        try:
            # https://stackoverflow.com/questions/66710047/
            # python-requests-library-get-the-status-code-without-downloading-the-target
            r = requests.get(
                self.url,
                timeout=self.timeout,
                verify=False,
                headers=self.__spoofing_headers__,
                allow_redirects=True,
            )
            self.status_code = r.status_code
            logger.debug(self.url + "\tStatus: " + str(r.status_code))
            self.response_headers = dict(r.headers)
            if r.status_code == 200:
                self.text = r.text
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
            LocationParseError,
        ) as e:
            logger.debug(f"got exception: {e}")
            self.request_error = True
            self.request_error_details = str(e)
        except (MissingSchema, InvalidSchema, InvalidURL, InvalidProxyURL) as e:
            logger.debug(f"got exception: {e}")
            self.malformed_url = True
            self.request_error = True
            self.request_error_details = str(e)

    def __check_url__(self):
        """IARI url checking"""
        # TODO deprecate __check_url__; use (future) __check_urls__ with single url arg instead
        logger.debug(f"Checking url: {self.url}")

        self.__get_dns_record__()
        self.__check_with_https_verify__()
        if self.request_error:
            self.__check_without_https_verify__()

    @property
    def __spoofing_headers__(self) -> Dict[str, str]:
        """We decided to use these headers because of https://github.com/internetarchive/wari/issues/698"""
        # From sawood at https://internetarchive.slack.com/archives/
        # C04PLJVSPAP/p1679596686133449?thread_ts=1679594636.835119&cid=C04PLJVSPAP
        return {
            "authority": "www.sciencedaily.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            # 'cookie': 'usprivacy=1YYN; usprivacy=1YYN; _ga_GT6V1PPT8H=GS1.1.1679596300.1.0.1679596300.60.0.0; _ga=GA1.1.787963363.1679596301',
            "dnt": "1",
            "if-modified-since": "Thu, 23 Mar 2023 14:24:45 GMT",
            "if-none-match": 'W/"329ecfdc8f2ee5caed98ffc465000dc9"',
            "referer": "https://github.com/internetarchive/ware/issues/6",
            "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        }

    def __detect_language__(self):
        handler = BaseHandler(text=self.text)
        handler.__detect_language__()
        # carry over attributes
        self.detected_language = handler.detected_language
        self.detected_language_error = handler.detected_language_error
        self.detected_language_error_details = self.detected_language_error_details

    @property
    def get_dict(self) -> Dict[str, Any]:
        url = self.dict()
        if self.malformed_url_details:
            url.update({"malformed_url_details": self.malformed_url_details.value})
        return url

    def __check_url_with_testdeadlink_api__(self):
        """This fetches the status code from the testdeadlink API of IABot"""
        from src import app

        testdeadlink_api_key = (
            os.getenv("TESTDEADLINK_KEY") if os.getenv("TESTDEADLINK_KEY") else ""
        )

        if not testdeadlink_api_key:
            # TODO: handle this better if api key missing
            app.logger.warning(
                "__check_url_with_testdeadlink_api__: Missing TESTDEADLINK environment variable, skipping check"
            )
        else:
            # call IABot's url status checker, testdeadlink
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }

            # replace any ampersands with %26, so that IABot includes all "&"s in the url check
            modified_url = self.url.replace("&", "%26")
            data = f"urls={modified_url}&authcode={testdeadlink_api_key}&returncodes=1"

            app.logger.info(
                f"__check_url_with_testdeadlink_api__: self.url is {self.url}"
            )

            response = requests.post(
                "https://iabot-api.archive.org/testdeadlink.php",
                headers=headers,
                data=data,
            )
            # get the status code
            if response.status_code == 200:
                data = response.json()
                print(data)
                # exit()
                if "results" in data:
                    # array of results
                    results = data["results"]
                    # Get the status code
                    for result in results:
                        # Skip if we get the errors first
                        if result != "errors":
                            # Get the status code
                            self.testdeadlink_status_code = results[result]
                            # Get any errors
                            if "errors" in results:
                                self.testdeadlink_error_details = results["errors"][
                                    result
                                ]
                            break

    def __check_url_with_searchurldata_api__(self):
        """This fetches the status code and other oinformation from the searchurldata API of IABot"""

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "http://en.wikipedia.org/wiki/User:GreenC via iabget.awk",
        }

        modified_url = urllib.parse.quote(self.url)  # url encode the url
        data = f"&action=searchurldata&urls={modified_url}"

        response = requests.post(
            "https://iabot.wmcloud.org/api.php?wiki=enwiki",
            headers=headers,
            data=data,
        )
        # get the status code
        if response.status_code == 200:
            data = response.json()
            print(data)
            # TODO handle return data or errors
            self.searchurldata_results = data
