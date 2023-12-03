import logging
from typing import Any, Dict, Optional

import validators  # type: ignore
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class WikipediaUrlArchive(BaseModel):
    # TODO may not need all this stuff just for archive url...
    # TODO ...we can just pass the url as is to iabot.

    """This models a URL in Wikipedia
    It uses BaseModel to avoid the cache
    attribute, so we can output it via the API easily

    We do not perform any checking or lookup here that requires HTTP requests.
    We only check based on the URL itself.
    """

    url: str

    @property
    def get_dict(self) -> Dict[str, Any]:
        url = self.dict()
        # if self.malformed_url_details:
        #     url.update({"malformed_url_details": self.malformed_url_details.value})
        return url

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

    def __lt__(self, other):
        return self.url < other.url
