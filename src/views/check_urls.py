import asyncio
import logging

# import hashlib
import os

# import re
# from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

import aiohttp
import requests
from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.models.api.job.check_urls_job import UrlsJob
from src.models.api.schema.check_urls_schema import UrlsSchema

# from src.models.exceptions import MissingInformationError
# from src.models.file_io.url_file_io import UrlFileIo
# from src.models.identifiers_checking.url import Url
from src.views.statistics.write_view import StatisticsWriteView

logger = logging.getLogger(__name__)


class CheckUrls(StatisticsWriteView):
    """
    This models all action based on requests from the frontend/patron
    It is instantiated at every request

    This view does not contain any of the checking logic.
    See src/models/checking
    """

    """
    UrlsJob returns a list of url's
    """
    job: Optional[UrlsJob] = None
    schema: Schema = UrlsSchema()
    serving_from_json: bool = False
    headers: Optional[Dict[str, Any]] = None
    #     {
    #     "Access-Control-Allow-Origin": "*",
    # }
    data: Optional[Dict[str, Any]] = None

    def get(self):
        """This is the main method and the entrypoint for flask
        Every branch in this method has to return a tuple (Any,response_code)"""
        from src import app

        app.logger.debug("get: running")
        self.__validate_and_get_job__()
        if self.job:
            return self.__return_results__()

    def __return_results__(self):
        from src import app

        app.logger.debug("__check_urls::__return_results__; running")

        data = {"contents": "iari/v2/check-urls"}

        self.urls_list = self.job.url_list
        self.urls_dict = {self.urls_list[i]: {} for i in range(len(self.urls_list))}

        results = self.__check_urls__()  # return dict of urls and their status/errors

        if "errors" in results:
            data["errors"] = results["errors"]

        if "results" in results:
            # move status codes from results to urls_dict
            for key, value in results["results"].items():
                if key in self.urls_dict:
                    # transfer value (which is status_code) to urls_dict entry
                    self.urls_dict[key] = value
                else:
                    app.logger.warning(
                        f'__check_urls__ results key "{key}" not found in source urls list'
                    )
                    # self.urls_dict[key] = value
                    # TODO add troublesome url to "trouble" list/dict data[] return property

        data["num_urls"] = len(self.urls_dict)
        data["urls"] = self.urls_dict

        # data["check_urls_raw_results"] = results

        timestamp = datetime.timestamp(datetime.utcnow())
        data["timestamp"] = int(timestamp)

        isodate = datetime.isoformat(datetime.utcnow())
        data["isodate"] = str(isodate)

        logger.debug(f"returning url data for {len(self.urls_dict)} links")

        return data, 200

    def __check_urls__(self):
        """
        fetches status codes of urls in self.url_dict
        Currently uses testdeadlink API of IABot

        returns { "error": <error text here>} if error:
        - TESTDEADLINK_KEY is missing  # TODO NB: this should raise an error and cause a fatal return
        """
        from src import app

        # process urls_list into skipped, cached, and search categories
        url_result_dict = {}
        search_urls = []

        for url in self.urls_list:  # basically, the "sorting hat" for urls

            # Check cache of url ::
            # ### TODO skipping for now...must implement for real!
            # self.__read_from_cache__()
            #         if self.io.data:
            #             - add url to "cached_urls" list (useless?)
            #             - url_resultss_dict[url] = <cached data>

            search_urls.append(url)

        # urls_response = self.__check_urls_with_iabot_async__(search_urls)
        urls_response = self.__check_urls_with_iabot__(search_urls)
        # urls_response assumed to be:
        # {
        #   "results"? : dict; keys: urls, values: { status_code: XXX, error? : True, error_details?: "..." }
        #   "errors"? : [ list of errors ]
        # }

        if "errors" in urls_response:
            return {"errors": urls_response["errors"]}

        if "results" in urls_response:
            # process iabot_response: move url status codes from results into url_result_dict
            for key, value in urls_response["results"].items():
                # save status of url in result_dict
                if key != "errors":
                    url_result_dict[key] = {
                        "status_code": value,
                    }

            # add any error info to urls in url_result_dict
            if "errors" in urls_response["results"]:
                for urlkey, value in urls_response["results"]["errors"].items():
                    # add error details to url entry
                    if urlkey not in url_result_dict:
                        url_result_dict[urlkey] = {}  # TODO: better syntax here?
                    url_result_dict[urlkey]["error"] = True
                    url_result_dict[urlkey]["error_details"] = value

            # and return dict, with status codes and errors, keyed by urls
            return {"results": url_result_dict}

    def __check_urls_with_iabot__(self, search_urls):
        """
        Example iabot response:
        {
            "results": {
                "http:\\/\\/www.estrellavalpo.cl\\/site\\/edic\\/20020611093623\\/pags\\/20020611124031.html": 302,
                "http:\\/\\/www.ethnologue.com\\/language\\/rap": 200,
                "https:\\/\\/orb.binghamton.edu\\/cgi\\/viewcontent.cgi?article=1041": 400,
                "errors": {
                    "https:\\/\\/orb.binghamton.edu\\/cgi\\/viewcontent.cgi?article=1041": "RESPONSE CODE: 400",
                    "https:\\/\\/www.britishmuseum.org\\/explore\\/highlights\\/highlight_objects\\/aoa\\/w\\/wooden_gorget_rei_miro.aspx": "RESPONSE CODE: 404"
                },
                "https:\\/\\/www.britishmuseum.org\\/explore\\/highlights\\/highlight_objects\\/aoa\\/w\\/wooden_gorget_rei_miro.aspx": 404
            },
            "servetime": 1.5802
        }

        example iabot error response:
        {
            "errors": {
                "error": f"Non 200 status code from testdeadlink call"
            }
        }
        """

        # TODO TODO chunk urls into 100 unit chinks, and process each chink till done.
        # error if no authcode available
        testdeadlink_api_key = self.__get_testdeadlink_api_key__()
        if not testdeadlink_api_key:
            # ### raise MissingInformationError("missing TESTDEADLINK_KEY")
            logger.warning(
                "Missing TESTDEADLINK environment variable, skipping IABot check"
            )
            return {
                "errors": [{"message": "Missing TESTDEADLINK_KEY environment variable"}]
            }

        # url_encode urls parameter - parmas cannot have any url-specific characters like "&", etc.
        import urllib.parse

        search_urls_param = urllib.parse.quote("\n".join(search_urls))

        # make the iabot call and respond accordingly
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        # TODO there should really be a "timeout" parameter sent to iabot/testdeadlink, but currently not supported
        data = f"urls={search_urls_param}&authcode={testdeadlink_api_key}&returncodes=1"

        response = requests.post(
            "https://iabot-api.archive.org/testdeadlink.php",
            headers=headers,
            data=data,
        )

        # process the results
        if response.status_code == 200:
            data = response.json()
            if "results" in data:
                # array of results
                return {"results": data["results"]}
            else:
                # TODO: raise an error here - should have results section
                return {"results": {}}

        else:
            logger.error(f"iabot error response: {response}")
            return {
                "errors": [
                    {
                        "status_code": response.status_code,
                        "message": f"Non 200 status code from testdeadlink call ({response.status_code})",
                        # "details": response,
                    }
                ]
            }

    # Function to check the status of a single URL asynchronously
    async def __check_url_status__(self, url, session):
        try:
            async with session.get(url) as response:
                # ### return f"{url} - Status Code: {response.status}"
                return {url: {"status_code": response.status}}
        except aiohttp.ClientError as e:
            # ### return f"{url} - Error: {str(e)}"
            return {url: {"status_code": 0, "error": True, "error_details": str(e)}}

    # Function to check the status of multiple URLs asynchronously
    async def __check_multiple_urls__(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.__check_url_status__(url, session) for url in urls]
            return await asyncio.gather(*tasks)

    # Create an event loop and call the function to check multiple URLs asynchronously
    def __check_urls_with_iabot_async__(self, urls):

        testdeadlink_api_key = self.__get_testdeadlink_api_key__()
        if not testdeadlink_api_key:
            # ### raise MissingInformationError("missing TESTDEADLINK_KEY")
            logger.warning(
                "Missing TESTDEADLINK environment variable, skipping IABot check"
            )
            return {
                "errors": [{"message": "Missing TESTDEADLINK_KEY environment variable"}]
            }

        # ??    loop = asyncio.get_event_loop()
        # ??    loop.run_until_complete(main()), or,
        # loop.run_until_complete(__check_urls_with_iabot_async__()) or
        # loop.run_until_complete( self.__check_multiple_urls__(urls) )

        url_statuses = self.__check_multiple_urls__(urls)
        # statuses are a mini dict: { <url>
        # Print the status of each URL
        print("RETURN STATUSES FROM __check_urls_with_iabot_async__")
        for status in url_statuses:
            print(status)

        # place the info of each url in urls_duct
        urls_dict = {}
        for status in url_statuses:
            urls_dict.update(status)  # status is a tiny dict: { <url> : { ... } }

        return urls_dict

    # if __name__ == "__main__":
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(main())

    def __get_testdeadlink_api_key__(self):
        return os.getenv("TESTDEADLINK_KEY") if os.getenv("TESTDEADLINK_KEY") else ""
        # TODO raise error here if not valid?


# @property
# def __url_hash_id__(self) -> str:
#     """This generates an 8-char long id based on the md5 hash of
#     the raw upper cased URL supplied by the user"""
#     if not self.job:
#         raise MissingInformationError()
#     return hashlib.md5(f"{self.job.unquoted_url.upper()}".encode()).hexdigest()[:8]
#
# def __setup_io__(self):
#     self.io = UrlFileIo(hash_based_id=self.__url_hash_id__)
#
# def __return_from_cache_or_analyze_and_return__(self):
#     from src import app
#
#     app.logger.debug("__handle_valid_job__; running")
#
#     if not self.job.refresh:
#         self.__setup_and_read_from_cache__()
#         if self.io.data:
#             return self.io.data, 200
#         else:
#             return self.__return_fresh_data__()
#     else:
#         return self.__return_fresh_data__()
#
# def __return_fresh_data__(self):
#     from src import app
#
#     url_string = self.job.unquoted_url
#     app.logger.info(f"Got {url_string}")
#     url = Url(url=url_string, timeout=self.job.timeout)
#     url.check()
#     data = url.get_dict
#     timestamp = datetime.timestamp(datetime.utcnow())
#     data["timestamp"] = int(timestamp)
#     isodate = datetime.isoformat(datetime.utcnow())
#     data["isodate"] = str(isodate)
#     url_hash_id = self.__url_hash_id__
#     data["id"] = url_hash_id
#     data_without_text = deepcopy(data)
#     del data_without_text["text"]
#     self.__write_to_cache__(data_without_text=data_without_text)
#     if self.job.refresh:
#         self.__print_log_message_about_refresh__()
#         data["refreshed_now"] = True
#     else:
#         data["refreshed_now"] = False
#     if self.job.debug:
#         return data, 200
#     else:
#         return data_without_text, 200
#
# def __write_to_cache__(self, data_without_text):
#     # We skip writes during testing
#     if not self.job.testing:
#         write = UrlFileIo(
#             data=data_without_text, hash_based_id=data_without_text["id"]
#         )
#         write.write_to_disk()
