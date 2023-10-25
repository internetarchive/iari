from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra

from src.models.wikimedia.enums import WikimediaDomain


class ArticleStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the patron wants from the article endpoint

    We use BaseModel to avoid the cache attribute"""

    wari_id: str = ""
    lang: str = "en"  # language code according to Wikimedia
    page_id: int = 0  # page id of the Wikipedia in question
    revision_id: int = 0
    revision_isodate: str = ""
    revision_timestamp: int = 0
    site: str = WikimediaDomain.wikipedia.value  # wikimedia site in question
    title: str = ""
    ores_score: Any = {}

    served_from_cache: bool = False
    timestamp: int = 0  # timestamp at beginning of analysis
    isodate: str = ""  # isodate (human readable) at beginning of analysis
    timing: int = 0  # time to analyze in seconds

    references: List[str] = []
    reference_statistics: Dict[str, int] = {}
    dehydrated_references: List[str] = []

    cite_refs_count: int = 0
    cite_refs: Optional[List] = []

    urls: List[str] = []
    fld_counts: Dict[str, int] = {}

    class Config:  # dead: disable
        extra = Extra.forbid  # dead: disable
