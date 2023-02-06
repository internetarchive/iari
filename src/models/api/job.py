import logging
from urllib.parse import quote, unquote

import requests
from pydantic import BaseModel

import config
from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.wikimedia.enums import WikimediaSite

logger = logging.getLogger(__name__)


class Job(BaseModel):
    """A generic job that can be submitted via the API"""

    lang: str = "en"
    site: WikimediaSite = WikimediaSite.wikipedia
    title: str
    testing: bool = False
    page_id: int = 0
    refresh: bool = False

    @property
    def quoted_title(self):
        if not self.title:
            raise MissingInformationError("self.title was empty")
        return quote(self.title, safe="")

    def get_page_id(self) -> None:
        from src.models.api import app

        app.logger.debug("get_page_id: running")
        if not self.page_id:
            if not self.lang or not self.title or not self.site:
                MissingInformationError()
            # https://stackoverflow.com/questions/31683508/wikipedia-mediawiki-api-get-pageid-from-url
            url = (
                f"https://{self.lang}.{self.site.value}.org/"
                f"w/api.php?action=query&format=json&titles={self.quoted_title}"
            )
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
                    f"Could not fetch page data from {self.site} because of 404. See {url}"
                )
            else:
                raise WikipediaApiFetchError(
                    f"Could not fetch page data. Got {response.status_code} from {url}"
                )

    def urldecode_title(self):
        """We decode the title to have a human readable string to pass around"""
        self.title = unquote(self.title)
