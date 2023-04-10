# from typing import Dict, List
#
# from pydantic import BaseModel
#
# from src.models.api.statistics.article.dehydrated_reference import DehydratedReference
# from src.models.api.statistics.article.reference_types import ReferenceTypes
#
#
# class ReferencesOverview(BaseModel):
#     """The purpose of this class is to model the statistics
#     the patron wants from the article endpoint
#
#     We give a highlevel overview of the references here using
#     dehydrated references to avoid returning all data at once
#     because there could be up 600+ references in total and that
#     would be a huge amount of data and we have a design principle
#     of keeping the return json small (ideally below 200 kb)
#
#     We use BaseModel to avoid the cache attribute"""
#
#     all: int
#     details: List[DehydratedReference] = []
#     first_level_domain_counts: Dict[str, int] = {}
#     types: ReferenceTypes
