from pydantic import BaseModel, Extra


class CheckUrlStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the patron wants from the article endpoint

    We use BaseModel to avoid the cache attribute"""

    refreshed_now: bool = False
    served_from_cache: bool = False
    timestamp: int = 0  # timestamp at beginning of analysis
    isodate: str = ""  # isodate (human readable) at beginning of analysis
    url: str
    status_code: int
    timeout: bool
    error: bool

    class Config:  # dead: disable
        extra = Extra.forbid  # dead: disable
