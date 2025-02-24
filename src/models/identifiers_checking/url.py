import logging
import os
import urllib.parse
from typing import Any, Dict, Optional

import requests

from src.models.api.handlers import BaseHandler
from src.models.wikimedia.wikipedia.url import WikipediaUrl

logger = logging.getLogger(__name__)


class Url(WikipediaUrl):
    """
    This handles checking a URL for it's http status

    We define a malformed URL as any URL that the reader cannot easily
    click and successfully get the contents of in a normal web browser session

    We send spoofing headers by default to avoid 4xx as much as possible
    and do not offer turning them off for now.
    """

    # iari test - deprecated, for now (2023.11.08)
    status_code: int = 0
    status_code_method: str = ""
    status_code_error_details: str = ""

    archive_status_method: str = ""
    archive_status: Optional[Dict] = None

    detected_language: str = ""
    detected_language_error: bool = False
    detected_language_error_details: str = ""

    timeout: int = 2

    text: str = ""

    # soft404_probability: float = 0.0  # not implemented yet

    # @property
    # def __check_soft404__(self):
    #     raise NotImplementedError()

    def check(self, method):
        from src import app

        if self.url:
            app.logger.debug(f"checking url with method {method}")

            self.extract()  # simple extractions from url (tld, etc.)

            self.status_code_method = method

            # each checking method sets
            #   status_code and
            #   status_code_error_details

            if method.upper() == "IABOT":
                self.__check_url_with_iabot_testdeadlink__()

            elif (method.upper() == "LIVEWEBCHECK" or
            method.upper() == "LWC" or
            method.upper() == "WAYBACK"):
                self.__check_url_with_livewebcheck_api__()

            elif method.upper() == "CORENTIN":
                self.__check_url_with_corentin_api__()

            else:
                # self.__error_with_method
                self.status_code_error_details = f"Unrecognized method: {method}"
                logger.info(f"Unrecognized method: {method}")

            # TODO provide for other archive methods here...
            self.archive_status_method = "iabot_searchurldata"
            self.__get_archive_status_with_iabot_api__()  # sets archive_status if successful
            self.__detect_language__()

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

    def __check_url_with_iabot_testdeadlink__(self):
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
                logger.debug(data)
                # exit()
                if "results" in data:
                    # array of results
                    results = data["results"]
                    # Get the status code
                    for result in results:
                        # Skip if we get the errors first
                        if result != "errors":
                            # Get the status code
                            # self.testdeadlink_status_code = results[result]
                            self.status_code = results[result]
                            # Get any errors
                            if "errors" in results:
                                self.status_code_error_details = results["errors"][
                                    result
                                ]
                            break

    def __check_url_with_livewebcheck_api__(self):
        """
        This use wayback machine's Live Web Checker
        response looks like:
        {
            "ctype": "text/html; charset=utf-8",
            "location": "https://mojomonger.com/",
            "status": 200,
            (optional) "status_ext" : "<error reason>  if error
            (optional) "message" : "<human readable error message>  if error
        }
        """

        endpoint = "https://iabot-api.archive.org/livewebcheck"
        modified_url = self.url.replace("&", "%26")  # TODO do appropriate encode
        headers = {}
        params = {
            "impersonate": 1,
            "skip-adblocker": 1,
            "url": modified_url,
        }

        response = requests.get(
            endpoint,
            headers=headers,
            params=params,
        )

        # get the status code
        if response.status_code == 200:
            data = response.json()
            logger.debug(data)
            if "status" in data:
                self.status_code = data["status"]
            if "status_ext" in data:
                self.status_code_error_details = data["status_ext"]

    def __check_url_with_corentin_api__(self):
        """
        This use corentin's link checker:

                endpoint: 'https://iabot-api.archive.org/undertaker/'

                const requestOptions = {
                    method: 'POST',
                    body: JSON.stringify({ urls: urlList })

        """
        self.status_code = 0
        self.status_code_error_details = "CORENTIN method not implemented in IARI"

    def __get_archive_status_with_iabot_api__(self):
        """
        This fetches the archive information using IABot's searchurldata
        """

        modified_url = urllib.parse.quote(self.url)  # url encode the url

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "http://en.wikipedia.org/wiki/User:GreenC via iabget.awk",
        }
        data = f"&action=searchurldata&urls={modified_url}"

        response = requests.post(
            "https://iabot.wmcloud.org/api.php?wiki=enwiki",
            headers=headers,
            data=data,
        )

        # if status code is 200, the request was successful
        if response.status_code == 200:
            data = response.json()
            # logger.debug(f"data for archive url:" + data)
            # TODO handle return data or errors
            self.archive_status = data
