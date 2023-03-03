# from pydantic import BaseModel
#
#
# class CiteJournalReferences(BaseModel):
#     """The purpose of this class is to model the statistics
#     the patron wants from the article endpoint
#
#     We use BaseModel to avoid the cache attribute"""
#
#     all: int
#     has_wm_url: int
#     has_url: int
#     has_doi: int
#     # wikidata: CiteJournalWikidataStatistics
#
#     class Config:  # dead: disable
#         extra = "forbid"  # dead: disable
