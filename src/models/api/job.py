from pydantic import BaseModel


class Job(BaseModel):
    """A generic job that can be submitted via the API"""

    lang: str
    site: str
    title: str
    testing: bool = False
