from typing import Dict, List

from pydantic import BaseModel

from src.models.api.get_statistics.references.links import Links
from src.models.api.get_statistics.references.reference_types import ReferenceTypes
from src.models.api.reference_statistics import ReferenceStatistics


class References(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    all: int
    details: List[ReferenceStatistics] = []
    links: Links
    types: ReferenceTypes
    first_level_domain_counts: List[Dict[str, int]] = []
