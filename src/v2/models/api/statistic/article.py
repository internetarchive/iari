from typing import Dict, List

from pydantic import BaseModel, Extra

from src.v2.models.wikimedia.enums import WikimediaDomain


class ArticleStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the patron wants from the article endpoint

    We use BaseModel to avoid the cache attribute"""

    wari_id: str = ""
    lang: str = "en"  # language code according to Wikimedia
    page_id: int = 0  # page id of the Wikipedia in question
    dehydrated_references: List[str] = []
    reference_statistics: Dict[str, int] = {}
    served_from_cache: bool = False
    site: str = WikimediaDomain.wikipedia.value  # wikimedia site in question
    timestamp: int = 0  # timestamp at beginning of analysis
    isodate: str = ""  # isodate (human readable) at beginning of analysis
    timing: int = 0  # time to analyze in seconds
    title: str = ""
    fld_counts: Dict[str, int] = {}
    urls: List[str] = []

    class Config:  # dead: disable
        extra = Extra.forbid  # dead: disable
