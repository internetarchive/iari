from typing import List

from pydantic import BaseModel

from src.models.wikimedia.wikipedia.url import WikipediaUrl


class Links(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    all: int
    s200: int
    s404: int
    s5xx: int
    other: int
    details: List[WikipediaUrl] = []
