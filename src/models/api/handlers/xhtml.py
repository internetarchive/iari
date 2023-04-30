import logging
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from src.models.api.job.check_url_job import UrlJob
from src.models.api.link.xhtml_link import XhtmlLink

logger = logging.getLogger(__name__)


class XhtmlHandler(BaseModel):
    """This class handles extraction of links from xhtml"""

    job: UrlJob
    content: bytes = b""
    links: List[XhtmlLink] = []
    error: bool = False
    error_details: str = ""

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    @property
    def total_number_of_links(self):
        return len(self.links)

    def __download_xhtml__(self):
        """Download XHTML file from URL."""
        # see https://stackoverflow.com/questions/23714383/what-are-all-the-possible-values-for-http-content-type-header
        valid_content_types = [
            "application/xhtml+xml",
            "text/html; charset=utf-8",
            "text/html",
        ]
        if not self.content:
            response = requests.get(self.job.url, timeout=self.job.timeout)
            content_type = response.headers["content-type"]
            if response.status_code != 200:
                self.error = True
                self.error_details = "Failed to download XHTML file from URL."
                logger.error(self.error_details)
                return
            # We keep strict to the types above for now
            if content_type.lower() not in valid_content_types:
                self.error = True
                self.error_details = (
                    f"Invalid content type for XHTML file. Got {content_type}"
                )
                logger.error(self.error_details)
                return
            self.content = response.content

    def __extract_links__(self) -> None:
        """Written by chatgpt and adjusted a little"""
        # extract all the links from the HTML content
        soup = BeautifulSoup(self.content, "lxml")
        for link in soup.find_all("a"):
            href = link.get("href")
            if href is not None:
                link_obj = XhtmlLink(
                    context=link,
                    href=href,
                    title=link.get("title", ""),
                    parent=link.parent,
                )
                self.links.append(link_obj)

    def download_and_extract(self):
        self.__download_xhtml__()
        if not self.error and not self.links:
            self.__extract_links__()

    def __get_links_dicts__(self) -> List[Dict[str, str]]:
        """This is needed to please the json encoder"""
        return [link.get_dict() for link in self.links]

    def get_dict(self):
        """Return data to the patron"""
        return dict(
            links=self.__get_links_dicts__(), links_total=self.total_number_of_links
        )
