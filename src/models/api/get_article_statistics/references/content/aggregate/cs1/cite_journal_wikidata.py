# from src.models.api.get_article_statistics.references.content.aggregate.wikidata import (
#     Wikidata,
# )
#
#
# class CiteJournalWikidata(Wikidata):
#     """The purpose of this class is to model the statistics
#     the user wants from the get_article_statistics endpoint
#
#     We use BaseModel to avoid the cache attribute"""
#
#     retracted: bool
#     has_url: int
#
#     class Config:
#         extra = "forbid"
