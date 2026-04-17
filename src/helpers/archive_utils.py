# probe_utils.py
from typing import Optional, Union

import requests

from src.helpers.cache_utils import get_cache, set_cache, is_cached, CacheType

from src.constants.constants import UrlArchiveMethod
from src.models.v2.probes.probe_test import ProbeTest
from src.models.v2.probes.probe_trust_project import ProbeTrustProject
from src.models.v2.probes.probe_verifyi import ProbeVerifyi

BASE_WAYBACK_CDX_URL = "https://web.archive.org/cdx/search/cdx"


def _get_response(self, url, params):
    try:
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        app.logger.error(f"Request failed: {e}.")
        # print(f"Request failed (attempt {retries}/{self.max_retries}): {e}. Retrying in {wait_time:.2f}s...")
        return {
            errors: [
                f"Wayback API Request failed: {e}"
            ]
        }
    # return None

def get_all_snapshots(url, from_year=None, to_year=None, limit=None, only_status_200=True):
    params = {
        "url": url,
        "output": "json",
        "fl": "timestamp,original,statuscode"
    }
    if from_year:
        params["from"] = from_year
    if to_year:
        params["to"] = to_year
    if limit:
        params["limit"] = limit
    if only_status_200:
        params["filter"] = "statuscode:200"

    data = _get_response(self.BASE_WAYBACK_CDX_URL, params)

    # if data["errors"] ....

    if not data or len(data) < 2:
        return []

    snapshots = []
    for row in data[1:]:
        snapshots.append({
            "timestamp": row[0],
            "url": f"{self.BASE_ARCHIVE_URL}/{row[0]}/{row[1]}",
            "statuscode": row[2]
        })
    return snapshots


def get_archive_status_iabot(url):
    """
    Fetch archive information for url
     - using IABot's searchurldata

    TODO: want to change this so it calls wayback archive status instead

    """

    import urllib.parse

    modified_url = urllib.parse.quote(url)  # url encode the url

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

    # Request successful if status code is 200
    if response.status_code == 200:
        data = response.json()
        # logger.debug(f"data for archive url:" + data)
        # TODO handle return data or errors
        return data
    else:
        return None


def get_archive_status_wayback(url, force_refresh=False):
    """
    Fetch archive information for url using wayback machine's search API
    """

    import urllib.parse

    modified_url = urllib.parse.quote(url)  # url encode the url

    # if archive status in cache, then return it

    # if cache exists for this domain, return that value
    if force_refresh == False and is_cached(modified_url, CacheType.archive, "wayback"):
        return_data = {
            "retrieved_from_cache": True,
        }

        archive = get_cache(modified_url, CacheType.archive, "wayback")
        return_data.update(archive)

        return return_data

    from src import app
    app.logger.debug(f"==> get_archive_status_wayback for {modified_url}")

# else fetch status from WAYBACK machine
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "http://en.wikipedia.org/wiki/User:GreenC via iabget.awk",
    }
    data = f"&url={modified_url}"

    response = requests.post(
        "https://archive.org/wayback/available",
        headers=headers,
        data=data,
    )


    # TODO
    #   save to cache if successful
    #       make sure to save data
    #   for now, skip


    # Request successful if status code is 200
    if response.status_code == 200:
        rawdata = response.json()
        app.logger.debug(f"==> get_archive_status_wayback for {modified_url} raw response from api: {rawdata}")

        if not rawdata or "results" not in rawdata or not rawdata["results"]:
            archive_data = {
                "archive_exists": False,
                "error": "No results found in Wayback API response"
            }
            return archive_data

        data = rawdata["results"][0]
        app.logger.debug(f"==> get_archive_status_wayback for {modified_url} extracted data: {data}")

        if not isinstance(data, dict) or "archived_snapshots" not in data:
            archive_data = {
                "archive_exists": False,
                "error": "Invalid data format in Wayback API response"
            }

        else:
            archived_snapshots = data.get("archived_snapshots", {})
    
            if not archived_snapshots:
                archive_data = {
                    "archive_exists": False,
                }

            else:    
                snapshot = archived_snapshots.get("closest", {})
                if snapshot:
                    archive_data = {
                        "archive_exists": True,
                        "archive_details": {
                            "status": snapshot.get("status"),
                            "available": snapshot.get("available"),
                            "url": snapshot.get("url"),
                            "timestamp": snapshot.get("timestamp")
                        }
                    }
                else:
                    archive_data = {
                        "archive_exists": False,
                        "error": "No snapshot data available"
                    }


    else:
        archive_data = {
            "archive_exists": False,
            "error": "Call failed from from Wayback API"
        }

    app.logger.debug(f"==> get_archive_status_wayback for {modified_url} returning: {archive_data}")

    # save archive in cache for this url
    set_cache(modified_url, CacheType.archive, "wayback", payload=archive_data)

    return archive_data



def get_archive_status(url, archive_method="wayback"):
    """
    """
    # return None

    if archive_method == "wayback":
        return get_archive_status_wayback(url)
    else:
        return None

    # if archive_method == UrlArchiveMethod.IABOT.value:
    #     return get_archive_status_iabot(url)
    # elif archive_method == "wayback":
    #     return get_archive_status_wayback(url)
    # else:
    #     return None