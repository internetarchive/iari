from typing import Any, Dict, List, Optional
from pathlib import Path
import requests
import config

from bs4 import BeautifulSoup

from src.models.v2.analyzers import IariAnalyzer

from src.helpers.iari_utils import iari_extract_root_domain
from src.helpers.signal_utils import get_signal_data_for_domain

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
        path = Path(f"{config.iari_cache_dir}/cache/{target_file_name}")
        app.logger.debug(f"GrokAnalyzer: fetch_page_html: use_local_cache: {path}")

        # if not there, return None ???
        if not path.exists():
            raise FileNotFoundError(
                f"GrokAnalyzer: fetch_page_html: Cache for file {target_file_name} not found ({path})."
            )

        return path.read_text(encoding="utf-8")  # return contents of file (hopefully html!)

    # if not cached, capture from live web
    user_agent = "IARI, see https://github.com/internetarchive/iari"
    target_url = f"https://grokipedia.com/page/{title}"
    headers = {"User-Agent": user_agent}

    app.logger.debug(f"GrokAnalyzer: fetch_page_html: requests.get({target_url})")

    response = requests.get(target_url, headers=headers)

    app.logger.debug(f"GrokAnalyzer: fetch_page_html: returned with status code: {response.status_code}")

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
    }

    TODO:
        raise Exception if errors occur along the way?

        or, if errors, return a dict:
        {
            "errors": errors,
        }
    """

    soup = BeautifulSoup(page_html, "html.parser")

    urls = []

    for a in soup.select("div#references > ol > li > div > span > a[href]"):
        href = a["href"]
        if href.startswith(("http://", "https://")):
            urls.append(href)

    final_urls = list(set(urls))  # deduplicate with set

    # Create dictionary with wiki signal data for each URL
    def create_url_dict_entry(url: str) -> Dict[str, Any]:
        domain = iari_extract_root_domain(url)
        signals = get_signal_data_for_domain(domain=domain, force_refresh=False)

        compact_signal_data = signals  # shall remove nullish entries
        return compact_signal_data

    url_dict = {url: create_url_dict_entry(url) for url in final_urls}

# send em back!
    return {
        "urls": final_urls,
        "url_dict": url_dict
    }
