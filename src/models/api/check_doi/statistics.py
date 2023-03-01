from pydantic import BaseModel, Extra


class CheckDoiStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the patron wants from the check-doi endpoint

    We use BaseModel to avoid the cache attribute"""

    refreshed_now: bool = False
    served_from_cache: bool = False
    timestamp: int = 0  # timestamp at beginning of analysis
    isodate: str = ""  # isodate (human readable) at beginning of analysis
    wikidata_entity_qid: str = ""
    openalex_work_uri: str = ""
    doi: str
    found_in_wikidata: bool = False
    found_in_openalex: bool = False
    marked_as_retracted_in_wikidata: bool = False
    marked_as_retracted_in_openalex: bool = False

    class Config:  # dead: disable
        extra = Extra.forbid  # dead: disable
