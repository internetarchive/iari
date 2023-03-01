from typing import Optional

from pydantic import BaseModel

from src.models.api.statistics.article.identifiers.urls_aggregates import UrlsAggregates


class Urls(BaseModel):
    """The purpose of this class is to model the statistics
    the patron wants from the article endpoint

    We use BaseModel to avoid the cache attribute"""

    agg: Optional[UrlsAggregates] = None
    urls_found: bool = False
    # The details are now found on each reference instead
    # details: List[WikipediaUrl] = []

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
