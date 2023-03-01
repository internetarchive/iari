from pydantic import BaseModel


class ReferencesCountStatistics(BaseModel):
    """This only returns the total number of references"""

    total: int

    class Config:
        extra = "forbid"
