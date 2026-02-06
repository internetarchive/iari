# status_utils.py
import requests
import urllib.parse

from src.constants.constants import UrlStatusMethod
from src.helpers.cache_utils import get_cache, set_cache, is_cached, CacheType


def get_live_status_for_url(url, force_refresh=False):
    """
    grabs live status for url using WAYBACK l

    returns:
    {
        "status_code", 999,
        "live_status_data:" { ... }  # raw descriptive fields
    }

    example: https://archive.org/wayback/available?url=http://libweb.hawaiiz.edu/digicoll/rapanui/Box13E01.html

    example return data for success (has an archive):

    {
      "root": {
        "url": "http://libweb.hawaii.edu/digicoll/rapanui/Box13E01.html",
        "archived_snapshots": {
          "closest": {
            "status": "200",
            "available": true,
            "url": "http://web.archive.org/web/20251223015723/https://libweb.hawaii.edu//digicoll/rapanui/Box13E01.html",
            "timestamp": "20251223015723"
          }
        }
      }
    }

    example return data if no archive present:

    {
      "root": {
        "url": "http://libweb.hawaiiz.edu/digicoll/rapanui/Box13E01.html"
        "archived_snapshots": {
        }
      }
    }

    """

    from src import app

    # if cache exists for this url's live status, return that value
    if force_refresh == False and is_cached(url, CacheType.status, variety=UrlStatusMethod.LIVEWEBCHECK.value):
        status = get_cache(url, CacheType.status, variety=UrlStatusMethod.LIVEWEBCHECK.value)
        return {
            "retrieved_from_cache": True,
            "live_status": status
        }

    # else fetch status using WAYBACK machine's livewebcheck
    live_status_code = __get_live_status_with_livewebcheck__(url)
    if live_status_code is not None:
        # save url status in cache for this url
        app.logger.debug(f"Set cache live-status for {url} to {live_status_code}")
        set_cache(url, CacheType.status, variety=UrlStatusMethod.LIVEWEBCHECK.value, payload=live_status_code)

    return {
        "live_status": live_status_code
    }


def __get_live_status_with_livewebcheck__(url):
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

    Currently this function returns just a status code (none or numerical)
    TODO pass back a status data dict so we can oass back errors and other details as well

    {
        status_code: 999.
    }
    """

    status_code = None

    endpoint = "https://iabot-api.archive.org/livewebcheck"
    modified_url = url.replace("&", "%26")  # TODO do appropriate encode
    # modified_url = urllib.parse.quote(url)  # url encode the url

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

        from src import app
        app.logger.debug(data)

        if "status" in data:
            status_code = data["status"]

        if "status_ext" in data:
            status_code = None
            # status_data = data["status_ext"]
            # self.status_code_error_details = data["status_ext"]

    return status_code
