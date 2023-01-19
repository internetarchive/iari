from pydantic import BaseModel


class CiteJournalReferences(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    all: int
    has_wm_link: int
    no_link: int
    has_doi: int
    # wikidata: CiteJournalWikidataStatistics
