from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra

from src.models.wikimedia.enums import WikimediaDomain


class ArticleStatisticsV2(BaseModel):
    """The purpose of this class is to model the statistics
    the patron wants from the article endpoint

    We use BaseModel to avoid the cache attribute"""

    iari_version: str = ""

    iari_id: str = ""
    page_errors: List[Any] = []

    lang: str = "en"  # language code according to Wikimedia
    site: str = WikimediaDomain.wikipedia.value  # wikimedia site in question
    title: str = ""
    page_id: int = 0  # page id of the Wikipedia in question

    revision_id: int = 0
    revision_isodate: str = ""
    revision_timestamp: int = 0

    served_from_cache: bool = False
    isodate: str = ""  # isodate (human readable) at beginning of analysis

    timestamp: int = 0  # timestamp at beginning of analysis
    timing: int = 0  # time to analyze in seconds

    ores_score: Any = {}

    reference_count: int = 0,
    reference_stats: Dict[str, int] = {},
    references: List[Dict[str, Any]] = [],
    url_count: int = 0,
    url_stats: Dict[str, Any] = {},
    urls: List[str] = [],

    # ores_score: Any = {}
    #
    # references: List[str] = []
    # reference_statistics: Dict[str, int] = {}
    #
    # urls: List[str] = []
    #
    # cite_refs_count: int = 0
    # cite_refs: Optional[List] = []
    #
    # fld_counts: Dict[str, int] = {}

    class Config:  # dead: disable
        extra = Extra.forbid  # dead: disable
