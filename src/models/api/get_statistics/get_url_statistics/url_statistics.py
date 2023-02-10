from typing import List, Optional

from pydantic import BaseModel, Extra

from src.models.api.get_statistics.references import References, Urls
from src.models.wikimedia.wikipedia.url import WikipediaUrl


class UrlStatistics(BaseModel):
    """The purpose of this class is to model the get_statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    lang: str = "en"  # language code according to Wikimedia
    page_id: int = 0  # page id of the Wikipedia in question
    refreshed_now: bool = False
    served_from_cache: bool = False
    site: str = "wikipedia"  # wikimedia site in question
    timestamp: int = 0  # timestamp at beginning of analysis
    isodate: str = ""  # isodate (human readable) at beginning of analysis
    timing: int = 0  # time to analyze in seconds
    title: str = ""
    url_details: List[WikipediaUrl] = []
    urls: Urls

    class Config:  # dead: disable
        extra = Extra.forbid  # dead: disable
