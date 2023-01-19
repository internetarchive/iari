from pydantic import BaseModel


class Wikidata(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    found: int
    has_fulltext: int
    disambiguated_authors: int
