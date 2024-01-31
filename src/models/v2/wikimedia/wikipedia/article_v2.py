import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

# from pydantic import validate_arguments
from bs4 import BeautifulSoup
from dateutil.parser import isoparse

import config
from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.v2.base import IariBaseModel
from src.models.v2.job.article_job_v2 import ArticleJobV2
from src.models.v2.wikimedia.wikipedia.reference.extractor_v2 import (
    WikipediaReferenceExtractorV2,
)
from src.models.wikimedia.enums import WikimediaDomain

logger = logging.getLogger(__name__)


class WikipediaArticleV2(IariBaseModel):
    """Models a Wikimedia Wikipedia article

    Mediawiki specifics:
    * A page has a permanent and stable page_id
    * Every edit creates a new revision that is incremented across all pages to a specific page_id

    Implementation details:
    Cache setup occurs only in this class and
    not in the classes below (ie Website and WikipediaReference)
    because of
    https://github.com/internetarchive/wcdimportbot/issues/261"""

    job: ArticleJobV2
    extractor: Optional[WikipediaReferenceExtractorV2] = None

    new_article_data: Dict[str, Any] = {}

    references: List[Dict[str, Any]] = []

    md5hash: Optional[str]
    page_id: int = 0
    wdqid: str = ""
    wikimedia_domain: WikimediaDomain = WikimediaDomain.wikipedia
    found_in_wikipedia: bool = True
    revision_isodate: Optional[datetime] = None
    revision_timestamp: int = 0

    wikitext: Optional[str]
    html_markup: Optional[str]

    ores_quality_prediction: str = ""
    ores_details: Dict = {}

    check_urls: bool = False
    testing: bool = False

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable
        extra = "forbid"  # dead: disable

    @property
    def is_redirect(self) -> bool:
        return "#REDIRECT" in str(self.wikitext)[:10]

    @property
    def revision_id(self) -> int:
        return self.job.revision or 0

    @property
    def url(self):
        return self.job.url

    def fetch_and_parse(self):
        """
        fetch embellished html for article
        parse this html for articles, etc.
        """
        from src import app

        app.logger.debug("ArticleV2::fetch_and_parse")
        app.logger.info("Fetching article data and parsing")

        if not self.wikitext:
            # fetch page data from Wikipedia if we don't already have wikitext
            # WTF why would we not have this?
            self.__fetch_wikitext__()

        if self.is_redirect:
            logger.debug(
                "Skipped extraction and parsing because the article is a redirect"
            )
            raise WikipediaApiFetchError("wiki article is a redirect")

        if not self.found_in_wikipedia:
            logger.debug(
                "Skipped extraction and parsing because the article was not found"
            )
            raise WikipediaApiFetchError("wiki article not found in wiki")

        if not self.wikitext:
            raise WikipediaApiFetchError("wikitext is empty")

        if not self.html_markup:
            self.__fetch_html__()

        self.__extract_references__()

        self.__get_ores_scores__()  # fills ores_quality_prediction and ores_details

    def __extract_references__(self):

        soup = BeautifulSoup(self.html_markup, "html.parser")
        # for link in soup.find_all("a"):
        #     print(link.get("href"))

        references_wrapper = soup.find("div", class_="mw-references-wrap")

        refs = []

        if references_wrapper:
            references_list = references_wrapper.find("ol", class_="references")
            ref_counter = 0
            for ref in references_list.find_all("li"):

                ref_counter += 1

                page_refs = []
                for link in ref.find_all("a"):
                    # span.mw-linkback-text children should have a citeref link
                    if link.find("span", class_="mw-linkback-text"):
                        page_refs.append(
                            {
                                "href": link.get("href"),
                                "id": link.get("id"),
                            }
                        )

                span_link = ref.find("span", class_="mw-reference-text")
                raw_data = None
                if span_link:
                    link_data = span_link.find("link")
                    if link_data:
                        raw_data = link_data.get("data-mw")

                refs.append(
                    {
                        "id": ref.get("id"),
                        "ref_index": ref_counter,
                        "raw_data": raw_data,
                        "page_refs": page_refs,
                    }
                )

        self.references = refs

    def __fetch_wikitext__(self) -> None:
        """This fetches metadata and the latest revision id
        and date from the MediaWiki REST v1 API if needed"""
        from src import app

        app.logger.debug("WikipediaArticleV2::__fetch_wikitext__: Running")
        self.__check_if_title_is_empty__()
        if not self.wikitext:
            if self.revision_id:
                self.__fetch_data_for_specific_revision__()
            else:
                self.__fetch_data_for_latest_revision__()

        else:
            logger.info(
                "Not fetching data via the Wikipedia REST API. We have already got all the data we need"
            )

    def __fetch_html__(self) -> None:
        """This fetches metadata and the latest revision id
        and date from the MediaWiki REST v1 API if needed"""
        from src import app

        app.logger.debug("WikipediaArticleV2::__fetch_html__")
        self.__check_if_title_is_empty__()

        # fetch html page data - sets self.html_markup
        self.__fetch_page_html__(self.revision_id)

    def __check_if_title_is_empty__(self):
        if not self.job.title:
            raise MissingInformationError("self.job.title was empty string")

    def __get_ores_scores__(self):

        if not self.revision_id:
            if self.job.testing:
                logger.warning(
                    "Not testing getting ores score during testing "
                    "when no revision_id or latest_revision_id are present"
                )
            else:
                raise MissingInformationError("No revision_id fetched, this is a bug")
        else:
            # get the latest ORES score via ORES API:
            #   https://ores.wikimedia.org/v3/scores/enwiki/234234320/articlequality
            # We only support Wikipedia for now
            wiki_project = f"{self.job.lang}wiki"
            response = requests.get(
                f"https://ores.wikimedia.org/v3/scores/{wiki_project}/{self.revision_id}/articlequality"
            )
            if response.status_code == 200:
                data = response.json()
                # console.print(data)
                string_id = str(self.revision_id)
                self.ores_quality_prediction = data[wiki_project]["scores"][string_id][
                    "articlequality"
                ]["score"]["prediction"]
                self.ores_details = data[wiki_project]["scores"][string_id][
                    "articlequality"
                ]["score"]
            else:
                print("Error:", response.status_code)

    def __fetch_data_for_specific_revision__(self):
        """Get wikitext for a specific revision

        Action-specific parameters

        titles= takes one or more titles for the query to operate on.

        pageids= takes one or more page ids for the query to operate on. revids= takes a list of revision IDs to work on.
        """
        from src import app

        app.logger.debug("__fetch_data_for_specific_revision__: running")
        url = (
            f"https://{self.job.lang}.{self.job.domain.value}/"
            f"w/rest.php/v1/revision/{self.job.revision}"
        )

        prop = "ids|timestamp|content"
        headers = {"User-Agent": config.user_agent}
        response = requests.get(
            url, params={"action": "query", "prop": prop}, headers=headers
        )
        # console.print(response.json())
        if response.status_code == 200:
            app.logger.debug("returned article data with prop: ids|timestamp|content")

            data = response.json()
            # self.revision_timestamp = data["timestamp"]
            self.revision_isodate = isoparse(data["timestamp"])
            self.revision_timestamp = round(self.revision_isodate.timestamp())
            self.page_id = data["page"]["id"]
            # logger.debug(f"Got pageid: {self.page_id}")
            self.wikitext = data["source"]

        elif response.status_code == 404:
            self.found_in_wikipedia = False
            logger.error(
                f"Could not fetch page data from {self.wikimedia_domain.name} because of 404. See {url}"
            )
        else:
            raise WikipediaApiFetchError(
                f"Could not fetch page data. Got {response.status_code} from {url}"
            )

    def __fetch_data_for_latest_revision__(self):
        # This is needed to support e.g. https://en.wikipedia.org/wiki/Musk%C3%B6_naval_base or
        # https://en.wikipedia.org/wiki/GNU/Linux_naming_controversy
        from src import app

        url = (
            f"https://{self.job.lang}.{self.job.domain.value}/"
            f"w/rest.php/v1/page/{self.job.quoted_title}"
        )
        headers = {"User-Agent": config.user_agent}
        response = requests.get(url, headers=headers)
        # console.print(response.json())
        if response.status_code == 200:
            data = response.json()
            self.job.revision = int(data["latest"]["id"])
            self.revision_isodate = isoparse(data["latest"]["timestamp"])
            self.revision_timestamp = round(self.revision_isodate.timestamp())
            self.page_id = int(data["id"])
            # logger.debug(f"Got pageid: {self.page_id}")
            self.wikitext = data["source"]

        elif response.status_code == 404:
            self.found_in_wikipedia = False
            app.logger.error(
                f"Could not fetch page data from {self.wikimedia_domain.name} because of 404. See {url}"
            )
        else:
            raise WikipediaApiFetchError(
                f"Could not fetch page data. Got {response.status_code} from {url}"
            )

    def __fetch_page_html__(self, revision_id=0):
        """
        Get html for wiki page as specified by
        """
        from src import app

        app.logger.debug("WikipediaArticleV2::__fetch_page_html__")

        # example request url for html source:
        # https://en.wikipedia.org/w/rest.php/v1/page/Earth/with_html
        url = (
            f"https://{self.job.lang}.{self.job.domain.value}/"
            f"w/rest.php/v1/page/{self.job.quoted_title}/with_html"
        )

        headers = {"User-Agent": config.user_agent}
        response = requests.get(url, headers=headers)

        # console.print(response.json())
        if response.status_code == 200:

            data = response.json()
            self.html_markup = data["html"]

        elif response.status_code == 404:
            # self.found_in_wikipedia = False
            logger.error(
                f"Could not fetch page html from {self.wikimedia_domain.name} because of 404. See {url}"
            )
            # NB TODO how to error here?
        else:
            raise WikipediaApiFetchError(
                f"Could not fetch page html. Got {response.status_code} from {url}"
            )
            # NB TODO how to error here?
