from pydantic import BaseModel

from src.models.api.statistics.article.identifiers.unique_urls_aggregates import (
    UniqueUrlsAggregates,
)


class UrlsAggregates(BaseModel):
    """This models the aggregates we want to know about the URLs found in the references"""

    all: int = 0
    unique: UniqueUrlsAggregates

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
