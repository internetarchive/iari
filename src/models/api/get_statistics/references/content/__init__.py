from pydantic import BaseModel

from src.models.api.get_statistics.references.content.aggregate import (
    AggregateContentReferences,
)
from src.models.api.get_statistics.references.content.citation_references import (
    CitationReferences,
)
from src.models.api.get_statistics.references.content.general_references import (
    GeneralReferences,
)


class ContentReferences(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    citation: CitationReferences
    general: GeneralReferences
    agg: AggregateContentReferences
