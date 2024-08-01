import logging
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from dateutil.parser import isoparse
from pydantic import validate_arguments

import config
from src.models.api.job.article_job import ArticleJob
from src.models.base import WariBaseModel
from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.wikimedia.enums import WikimediaDomain
from src.models.wikimedia.wikipedia.reference.extractor import (
    WikipediaReferenceExtractor,
)

logger = logging.getLogger(__name__)


class WikipediaArticle(WariBaseModel):
    """Models a WMF Wikipedia article

    Mediawiki specifics:
    * A page has a permanent and stable page_id
    * Every edit creates a new revision that is incremented across all pages to a specific page_id

    Implementation details:
    Cache setup occurs only in this class and
    not in the classes below (ie Website and WikipediaReference)
    because of
    https://github.com/internetarchive/wcdimportbot/issues/261"""

    job: ArticleJob

    md5hash: Optional[str]
    page_id: int = 0
    wdqid: str = ""
    wikimedia_domain: WikimediaDomain = WikimediaDomain.wikipedia
    found_in_wikipedia: bool = True
    revision_isodate: Optional[datetime] = None
    revision_timestamp: int = 0

    wikitext: Optional[str]
    html_markup: Optional[str]

    extractor: Optional[WikipediaReferenceExtractor] = None
    # extractor: Optional[Any] = None
    # TODO: FIXFIX

    ores_quality_prediction: str = ""
    ores_details: Optional[Dict] = None

    check_urls: bool = False
    testing: bool = False

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable
        extra = "forbid"  # dead: disable

    # @property
    # def absolute_url(self):
    #     return f"https://{self.language_code}.{self.wikimedia_site.value}.org/w/index.php?curid={self.page_id}"

    @property
    def is_redirect(self) -> bool:
        return "#REDIRECT" in str(self.wikitext)[:10]

    # @property
    # def underscored_title(self):
    #     """Helper property"""
    #     if not self.job.title:
    #         raise ValueError("self.title was empty")
    #     return self.job.title.replace(" ", "_")

    @property
    def revision_id(self) -> int:
        return self.job.revision or 0

    @property
    def url(self):
        return self.job.url

    # @property
    # def wikibase_url(self):
    #     if self.wikibase.item_prefixed_wikibase:
    #         return f"{self.wikibase.wikibase_url}wiki/Item:{self.return_.item_qid}"
    #     else:
    #         return f"{self.wikibase.wikibase_url}wiki/{self.return_.item_qid}"

    # def __generate_hash__(self):
    #     hashing = Hashing(article=self, testing=True)
    #     self.md5hash = hashing.generate_article_hash()

    def fetch_and_extract_and_parse(self):
        from src import app

        app.logger.debug("==> WikipediaArticle::fetch_and_extract_and_parse")

        if not self.wikitext:
            # fetch page data from Wikipedia if we don't already have wikitext
            self.__fetch_page_data__()

        if self.is_redirect:
            logger.debug(
                "Skipped extraction and parsing because the article is a redirect"
            )

        elif not self.found_in_wikipedia:
            logger.debug(
                "Skipped extraction and parsing because the article was not found"
            )
        elif not self.is_redirect and self.found_in_wikipedia:
            if not self.wikitext:
                raise MissingInformationError("self.wikitext was empty")

            # We got what we need now to make the extraction and parsing
            # print(self.wikitext)
            # from src.models.wikimedia.wikipedia.reference.extractor import (
            #     WikipediaReferenceExtractor,
            # )
            # TODO: FIXFIX

            app.logger.debug("pulling in extractor")

            self.extractor = WikipediaReferenceExtractor(
                wikitext=self.wikitext,
                html_source=self.html_markup,
                # wikibase=self.wikibase,
                job=self.job,
            )

            # raise MissingInformationError("HoHum!")

            self.extractor.extract_all_references()
            self.__get_ores_scores__()
            # self.__generate_hash__()
        else:
            raise Exception("This branch should never be hit.")

    def __fetch_page_data__(self) -> None:
        """This fetches metadata and the latest revision id
        and date from the MediaWiki REST v1 API if needed"""
        from src import app

        app.logger.debug("==> __fetch_page_data__: Running")

        self.__check_if_title_is_empty__()
        if not self.wikitext:
            if self.revision_id:
                self.__fetch_data_for_specific_revision__()
            else:
                self.__fetch_data_for_latest_revision__()

            # now fetch html data
            self.__fetch_page_html__()

        else:
            logger.info(
                "Not fetching data via the Wikipedia REST API. We have already got all the data we need"
            )

    def __parse_templates__(self):
        """Disabled method because of rewrite"""

    @validate_arguments
    def __get_wikipedia_article_from_wdqid__(self):
        raise DeprecationWarning("deprecated because of failed test since 2.1.0-alpha2")
        # self.__get_title_from_wikidata__()
        # self.__get_wikipedia_article_from_title__()

    def __get_title_from_wikidata__(self):
        raise DeprecationWarning("deprecated because of failed test since 2.1.0-alpha2")

    def __check_if_title_is_empty__(self):
        if not self.job.title:
            raise MissingInformationError("WikipediaArticle: self.job.title is empty")

    def __get_ores_scores__(self):
        self.ores_details = {}
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

    def __fetch_page_html__(self):
        """Get html for latest version of page

        We do this in order to fetch the cite-ref's for each reference

        """
        from src import app

        app.logger.debug("__fetch_page_html__: running")

        # page request url for html source:
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
        else:
            raise WikipediaApiFetchError(
                f"Could not fetch page html. Got {response.status_code} from {url}"
            )
