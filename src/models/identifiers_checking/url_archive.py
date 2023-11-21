import logging
import urllib.parse
from typing import Any, Dict, Optional

import requests

from src.models.wikimedia.wikipedia.url_archive import WikipediaUrlArchive

logger = logging.getLogger(__name__)


class UrlArchive(WikipediaUrlArchive):
    """
    This handles checking a URL for it's http status

    We define a malformed URL as any URL that the reader cannot easily
    click and successfully get the contents of in a normal web browser session

    We send spoofing headers by default to avoid 4xx as much as possible
    and do not offer turning them off for now.
    """

    # IABot Archive information (from internal iabot database)
    iabot_results: Optional[Dict] = None

    def check(self):
        if self.url:
            # self.extract()
            self.__check_url_archive_with_iabot_api__()

    @property
    def get_dict(self) -> Dict[str, Any]:
        url = self.dict()
        # if self.malformed_url_details:
        #     url.update({"malformed_url_details": self.malformed_url_details.value})
        return url

    def __check_url_archive_with_iabot_api__(self):
        """
        This fetches the archive information using IABot's searchurldata
        """

        modified_url = urllib.parse.quote(self.url)  # url encode the url

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

        # if status code is 200, the request was successful
        if response.status_code == 200:
            data = response.json()
            print(data)
            # TODO handle return data or errors
            self.iabot_results = data
