import logging

import requests
from pydantic import BaseModel
from tld import get_fld
from tld.exceptions import TldBadUrl

logger = logging.getLogger(__name__)


class WikipediaUrl(BaseModel):
    """This models a URL
    It uses BaseModel to avoid the cache
    attribute so we can output it via the API easily"""

    soft404_probability: float = 0.0
    url: str
    checked: bool = False
    status_code: int = 0
    first_level_domain: str = ""

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

    @property
    def check_soft404(self):
        raise NotImplementedError()

    def check(self):
        r = requests.get(self.url)
        self.status_code = r.status_code
        logger.debug(self.url + "\tStatus: " + str(r.status_code))
        # if r.status_code == 200:
        #     self.check_soft404
        self.checked = True

    def is_google_books_url(self):
        return bool("//books.google." in self.url)

    def is_wayback_machine_url(self):
        return bool("//web.archive.org" in self.url)

    def is_ia_details_url(self):
        """Checks for Internet Archive details url"""
        return bool("//archive.org/details" in self.url)

    def get_first_level_domain(self):
        logger.debug("__get_first_level_domain__: Running")
        try:
            logger.debug(f"Trying to get FLD from {self.url}")
            fld = get_fld(self.url)
            if fld:
                logger.debug(f"Found FLD: {fld}")
                self.first_level_domain = fld
        except TldBadUrl:
            """The library does not support Wayback Machine URLs"""
            if self.is_wayback_machine_url():
                return "archive.org"
            else:
                message = f"Bad url {self.url} encountered"
                logger.warning(message)
                # self.__log_to_file__(
                #     message=str(message), file_name="url_exceptions.log"
                # )
                # return None
