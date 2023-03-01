from pydantic import BaseModel


class UniqueUrlsAggregates(BaseModel):
    all: int = 0
    malformed_urls: int = 0

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
