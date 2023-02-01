from typing import Optional

from pydantic import BaseModel, Extra

from src.models.api.get_article_statistics.references import References


class ArticleStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    has_references: bool = False
    lang: str = "en"  # language code according to Wikimedia
    page_id: int = 0  # page id of the Wikipedia in question
    references: Optional[References] = None
    served_from_disk: bool = False
    site: str = "wikipedia"  # wikimedia site in question
    timestamp: int = 0  # timestamp at beginning of analysis
    timing: int = 0  # time to analyze in seconds
    title: str = ""

    class Config:
        extra = Extra.forbid
