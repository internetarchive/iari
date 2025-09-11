# status_utils.py
import requests

from src.constants.constants import UrlStatusMethod
from src.helpers.cache_utils import get_cache, set_cache, is_cached, CacheType


class StatusUtils:


    @staticmethod
    def get_status_results(url_link: str, status_method: str, refresh: bool = False):
        """
        returns http status for url_link using status_method supplied
        """

        from src import app
        app.logger.debug([f"==> get_status_results: url_link: {url_link}",
                          f", status_method: {status_method}"
                          f", refresh = {str(refresh)}"])

        status_results = {}

        if refresh:
            """
            if refresh:
                fetch status anew, and save new data in cache for url/status_method pair
            """

            new_data = StatusUtils.get_status_data(url_link, status_method)
            # TODO NB what to do if new_data is error?
            #   may want to keep cache as is if already there,
            #   and "send back" error as response
            #   basically, not save to cache if error

            # TODO have some way of tagging status data with a timestamp of access date
            set_cache(url_link, CacheType.status, status_method, new_data)

        else:
            """
            if not refresh:
                check if url has status data for status_method i cache already
                if is_cached, do nothing, as cache already exists for status-url pair
                if not is_cached
                    fetch status(url)
                    set_cache status-url
            """
            if not is_cached(url_link, CacheType.status, status_method):
                new_data = StatusUtils.get_status_data(url_link, status_method)

                # TODO NB what to do if new_data is error?
                #
                # do not save errors in cache!
                #
                # IDEA: set_cache can behave like a "store another snapshot". This will give us a way
                #   to have a sort of database of cached fetches, to have a hotory
                #   we probably should have a comparison so we dont resave same data, but should
                #   at least save a "snapshot" date if multiple fetches produce same results

                set_cache(url_link, CacheType.status, status_method, new_data)

            else:  # data for probe p is cached, so use it
                new_data = get_cache(url_link, CacheType.status, status_method)


        # # gather all cached probe results into probe_results, regardless of refresh status
        # """
        # in either case of refresh:
        #     gather all probes from cache
        #     calc score
        #     return: { score:<xxx>, probe_results{ a: <xxx>, b: <xxx>, c: <xxx> }
        # """
        # for p in probe_list:
        #     data = get_cache(url_link, CacheType.probes, p)
        #     probe_results[p] = data

        return new_data


    @staticmethod
    def get_status_data(url, status_method):
        """
        fetch status data for specified url
        """

        results = {
            "url": "xyz.com",
            "status_method": status_method,
            "status_code": 0,
            "other_stuff": "other stuff goes here, like url parts, archive status, etc"
        }

        try:
            # TODO: these specific implementations of status codes should eventually be in their
            #     own modules, and we can select which one to use with the Strategy pattern
            #

            # LIVEWEBCHECK method
            if status_method.upper() == UrlStatusMethod.LIVEWEBCHECK.value:
                results = StatusUtils.check_url_with_livewebcheck_api(url)


            # we should be able to re-use the methods in identifiers_checking/url and Wikipedia/Url to
            # get the status info for a URL

            # try:
            #     # TEST method
            #     if status_method.upper() == UrlStatusMethod.IABOT.value:
            #         results = ProbeTest.probe(url=url)
            #
            #     # VERIFYI method
            #     elif probe_name.upper() == ProbeMethod.VERIFYI.value:
            #         results = ProbeVerifyi.probe(url=url)
            #
            #     # TRUST_PROJECT method
            #     elif probe_name.upper() == ProbeMethod.TRUST_PROJECT.value:
            #         results = ProbeTrustProject.probe(url=url)
            #

            # status method not supported
            else:
                results = {
                    "errors": [
                        f"Unknown status method: {status_method}"
                    ]
                }

        except Exception as e:
            results = {
                "errors": [
                    f"Error checking status with method {status_method} ({str(e)})."
                ]
            }

        return results


    @staticmethod
    def check_url_with_livewebcheck_api(url: str):
        """
        TODO: these specific implementations of status codes should eventually be in their
            own modules, and we can select which one to use with the Strategy pattern

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
        modified_url = url.replace("&", "%26")  # TODO do appropriate encode
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

        results = {}

        # get the status code
        if response.status_code == 200:
            data = response.json()
            if "status" in data:
                results.update({
                    "status_code", data["status"]
                })
            if "status_ext" in data:
                results.update({
                    "status_code_error_details", data["status_ext"]
                })

        return results