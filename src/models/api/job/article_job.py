import re
from urllib.parse import quote, unquote

import requests

import config
from src.models.api.enums import Lang
from src.models.api.job import Job
from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.wikimedia.enums import WikimediaDomain


class ArticleJob(Job):
    """A generic job that can be submitted via the API"""

    lang: Lang = Lang.en
    domain: WikimediaDomain = WikimediaDomain.wikipedia
    title: str = ""
    testing: bool = False
    page_id: int = 0
    refresh: bool = False
    url: str = ""

    @property
    def quoted_title(self):
        if not self.title:
            raise MissingInformationError("self.title was empty")
        return quote(self.title, safe="")

    def get_page_id(self) -> None:
        from src.models.api import app

        app.logger.debug("get_page_id: running")
        if not self.page_id:
            if not self.lang or not self.title or not self.domain:
                raise MissingInformationError()
            # https://stackoverflow.com/questions/31683508/wikipedia-mediawiki-api-get-pageid-from-url
            url = (
                f"https://{self.lang.value}.{self.domain.value}/"
                f"w/api.php?action=query&format=json&titles={self.quoted_title}"
            )
            app.logger.debug(f"api url: {url}")
            headers = {"User-Agent": config.user_agent}
            response = requests.get(url, headers=headers)
            # console.print(response.json())
            if response.status_code == 200:
                data = response.json()
                query = data.get("query")
                if query:
                    pages = query.get("pages")
                    if pages:
                        for page in pages:
                            if page:
                                app.logger.info("Got page id")
                                self.page_id = int(page)
            elif response.status_code == 404:
                app.logger.error(
                    f"Could not fetch page data from {self.domain} because of 404. See {url}"
                )
            else:
                raise WikipediaApiFetchError(
                    f"Could not fetch page data. Got {response.status_code} from {url}"
                )

    def urldecode_title(self):
        """We decode the title to have a human readable string to pass around"""
        self.title = unquote(self.title)

    def __urldecode_url__(self):
        """We decode the title to have a human readable string to pass around"""
        self.url = unquote(self.url)

    def extract_url(self):
        """This was generated with help of chatgpt using this prompt:
        I want a python re regex that extracts "en" "wikipedia.or"
        and "Test" from http://en.wikipedia.org/wiki/Test
        """
        if self.url:
            self.__urldecode_url__()
            pattern = r"https?://(\w+)\.(\w+\.\w+)/wiki/(.+)"

            matches = re.match(pattern, self.url)
            if matches:
                groups = matches.groups()
                self.lang = Lang(groups[0])
                self.domain = WikimediaDomain(groups[1])
                self.title = groups[2]
