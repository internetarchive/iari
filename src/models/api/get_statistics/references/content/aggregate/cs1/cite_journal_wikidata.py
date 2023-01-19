from src.models.api.get_statistics.references.content.aggregate.wikidata import Wikidata


class CiteJournalWikidata(Wikidata):
    """The purpose of this class is to model the statistics
    the user wants from the get_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    retracted: bool
