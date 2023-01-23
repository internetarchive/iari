from typing import Dict, List

from pydantic import BaseModel

from src.models.api.get_article_statistics.reference_statistics import (
    ReferenceStatistics,
)
from src.models.api.get_article_statistics.references.links import Links
from src.models.api.get_article_statistics.references.reference_types import (
    ReferenceTypes,
)


class References(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    all: int
    details: List[ReferenceStatistics] = []
    first_level_domain_counts: List[Dict[str, int]] = []
    links: Links
    types: ReferenceTypes
