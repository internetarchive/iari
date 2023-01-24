from typing import List, Optional

from pydantic import BaseModel

from src.models.api.get_article_statistics.references.links_aggregates import (
    LinksAggregates,
)
from src.models.wikimedia.wikipedia.url import WikipediaUrl


class Links(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    agg: Optional[LinksAggregates] = None
    links_found: bool = False
    malformed_urls: int = 0
    details: List[WikipediaUrl] = []
