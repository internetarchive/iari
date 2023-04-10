# from pydantic import BaseModel
#
# from src.models.api.deprecated.content.aggregate.cs1.cite_book_references import (
#     CiteBookReferences,
# )
# from src.models.api.deprecated.content.aggregate.cs1.cite_journal_references import (
#     CiteJournalReferences,
# )
# from src.models.api.deprecated.content.aggregate.cs1.cite_web_references import (
#     CiteWebReferences,
# )
#
#
# class Cs1References(BaseModel):
#     """The purpose of this class is to model the statistics
#     the patron wants from the article endpoint
#
#     We use BaseModel to avoid the cache attribute"""
#
#     # Number of references where we detected a CS1 templates, see https://en.wikipedia.org/wiki/Help:Citation_Style_1
#     # Transclusion statistics:
#     all: int
#     # cite web 4420k pages
#     web: CiteWebReferences
#     # cite journal 912k pages
#     journal: CiteJournalReferences
#     # cite book 1.520M pages
#     book: CiteBookReferences
#     others: int
