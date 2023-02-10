from pydantic import BaseModel


class CiteJournalReferences(BaseModel):
    """The purpose of this class is to model the get_statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    all: int
    has_wm_url: int
    has_url: int
    has_doi: int
    # wikidata: CiteJournalWikidataStatistics

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
