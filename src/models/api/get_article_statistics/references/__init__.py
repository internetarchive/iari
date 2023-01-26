from typing import Dict, List

from pydantic import BaseModel

from src.models.api.get_article_statistics.references.reference_statistics import (
    ReferenceStatistics,
)
from src.models.api.get_article_statistics.references.reference_types import (
    ReferenceTypes,
)
from src.models.api.get_article_statistics.references.urls import Urls


class References(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    all: int
    details: List[ReferenceStatistics] = []
    first_level_domain_counts: List[Dict[str, int]] = []
    urls: Urls
    types: ReferenceTypes
