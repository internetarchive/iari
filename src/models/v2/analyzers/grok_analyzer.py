from typing import Any, Dict, List, Optional
from pathlib import Path
import requests
import config

from bs4 import BeautifulSoup

from src.models.v2.analyzers import IariAnalyzer
from src.constants.constants import UrlArchiveMethod

from src.helpers.iari_utils import iari_extract_root_domain
from src.helpers.signal_utils import get_signal_data_for_domain_old, filter_signal_data_old
from src.helpers.archive_utils import get_archive_status
# from src.helpers.status_utils import get_live_status, get_live_status_for_url
from src.helpers.status_utils import get_live_status_for_url


class GrokAnalyzerV2(IariAnalyzer):
    """
    "Implements" IariAnalyzer base class

    logic for getting statistics from wiki page

    what we need:
        page spec or wikitext

    what we return:
        json formatted data of refs
        NB: later: more statistical data from refs

    """

    @staticmethod
    def extract_page_data(page_spec) -> Dict[str, Any]:
        """
        parse out urls from grokipedia article

        NB: Does not do any exception handling
        """

        from src import app

        # seed return data
        payload = {
            "media_type": "grokipedia_article"
        }
        payload.update(page_spec)

        title = page_spec["page_title"].replace(" ", "_")
        use_local_cache = page_spec["use_local_cache"]

        app.logger.debug(f"GrokAnalyzer: ***** extract_page_data: use_local_cache: {use_local_cache}")

        # fetch html from grokipedia file
        page_html = fetch_page_html(title, use_local_cache)
        page_data = extract_grok_data(page_html)

        payload["url_count"] = len(page_data["urls"])
        payload["urls"] = page_data["urls"]
        payload["url_dict"] = page_data["url_dict"]

        return payload


def fetch_page_html(title, use_local_cache : bool = False):
    """
    Return html of latest grokipedia page specified by title
    if use_local_cache is true, content is fetched from cache
    """
    from src import app

    app.logger.debug(f"GrokAnalyzer: ***** fetch_page_html: use_local_cache: {use_local_cache}")

    if use_local_cache:
        target_file_name = f"grokipedia.page.{title.replace(' ', '-')}.html"
        path = Path(f"{config.iari_cache_dir}{target_file_name}")
        app.logger.debug(f"GrokAnalyzer: ***** fetch_page_html: using local cache of: {path}")

        # if not there, return None ???
        if not path.exists():
            raise FileNotFoundError(
                f"GrokAnalyzer: fetch_page_html: Cache for file {target_file_name} not found (file path: {path})."
            )

        app.logger.debug(f"GrokAnalyzer: ***** returning local cache for: {path}")
        # app.logger.debug(f"GrokAnalyzer: path.read_text {path.read_text()}")
        # return path.read_text(encoding="utf-8")  # return contents of file (hopefully html!)
        return path.read_text()  # return contents of file (hopefully html!)

    # if not cached, capture from live web
    user_agent = "IARI, see https://github.com/internetarchive/iari"
    target_url = f"https://grokipedia.com/page/{title}"
    headers = {"User-Agent": user_agent}

    app.logger.debug(f"GrokAnalyzer: fetch_page_html: requests.get({target_url})")

    response = requests.get(target_url, headers=headers)

    app.logger.debug(f"GrokAnalyzer: fetch_page_html: returned with status code: {response.status_code}")
    app.logger.debug(f"response.encoding: {response.encoding}")
    app.logger.debug(f"response.apparent_encoding: {response.apparent_encoding}")

    if response.status_code == 200:
        response.raise_for_status()
        return response.text

    else:
        raise Exception(
            f"Got {response.status_code} response code when fetching grokipedia page: {title}. ({target_url})"
        )


def extract_grok_data(page_html) -> Dict[str, Any]:

    """
    returns a dict describing page and references
    for now, just returns urls from refs
    {
        "urls": list of urls in references section
        "url_dict": dictionary of data for each url, including signal data and archive status
    }

    TODO:
        raise Exception if errors occur along the way?

        or, if errors, return a dict:
        {
            "errors": errors,
        }
    """

    def create_dict_for_url(url: str, idx: int) -> Dict[str, Any]:

        # signal data based on domain of url link
        domain = iari_extract_root_domain(url)
        signal_data = get_signal_data_for_domain_old(domain=domain, force_refresh=False)
        if 'signals' in signal_data:
            filtered_signals = filter_signal_data_old(signal_data["signals"], "remove_nulls")
            signal_data["signals"] = filtered_signals

        # archive_status = {"archive_status": True}
        archive_status = get_archive_status(url, "wayback")

        # from src import app
        # app.logger.debug(f"==> create_dict_for_url:: {url}, archive_status: {archive_status}")
        live_status_data = get_live_status_for_url(url, force_refresh=False)  # add refresh=True if refresh set
        live_status = live_status_data.get("live_status", None)  # Use .get() with default None if key missing

        return {
            "signal_data": signal_data,
            "archive_data": archive_status,
            "live_status": live_status,
            "idx": idx
        }

    # extract list of reference links from References section of article
    soup = BeautifulSoup(page_html, "html.parser")
    urls = []
    for a in soup.select("div#references > ol > li > div > span > a[href]"):
        href = a["href"]
        if href.startswith(("http://", "https://")):
            urls.append(href)
    final_urls = list(set(urls))  # deduplicate with set

    # Create a wiki signal dictionary for each URL in final_urls
    url_dict = {url: create_dict_for_url(url, idx + 1) for idx, url in enumerate(final_urls)}

    from src import app
    app.logger.debug(f"==> extract_grok_data:: processed {len(url_dict)} urls")

    # send em back!
    return {
        "urls": final_urls,
        "url_dict": url_dict
    }
