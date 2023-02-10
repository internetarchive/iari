from pydantic import BaseModel

from src.models.api.get_statistics.references.content.aggregate.cs1.cite_book_references import (
    CiteBookReferences,
)
from src.models.api.get_statistics.references.content.aggregate.cs1.cite_journal_references import (
    CiteJournalReferences,
)
from src.models.api.get_statistics.references.content.aggregate.cs1.cite_web_references import (
    CiteWebReferences,
)


class Cs1References(BaseModel):
    """The purpose of this class is to model the get_statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    # Number of references where we detected a CS1 template, see https://en.wikipedia.org/wiki/Help:Citation_Style_1
    # Transclusion get_statistics:
    all: int
    # cite web 4420k pages
    web: CiteWebReferences
    # cite journal 912k pages
    journal: CiteJournalReferences
    # cite book 1.520M pages
    book: CiteBookReferences
    others: int
