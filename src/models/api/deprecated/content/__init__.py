# from pydantic import BaseModel
#
# from src.models.api.deprecated.content.aggregate import (
#     AggregateContentReferences,
# )
# from src.models.api.deprecated.content.citation_references import (
#     CitationReferences,
# )
# from src.models.api.deprecated.content.general_references import (
#     GeneralReferences,
# )
#
#
# class ContentReferences(BaseModel):
#     """The purpose of this class is to model the statistics
#     the patron wants from the article endpoint
#
#     We use BaseModel to avoid the cache attribute"""
#
#     all: int
#     citation: CitationReferences
#     general: GeneralReferences
#     agg: AggregateContentReferences
#
#     class Config:  # dead: disable
#         extra = "forbid"  # dead: disable
