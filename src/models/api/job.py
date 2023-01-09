from urllib.parse import unquote

from pydantic import BaseModel

from src.models.wikimedia.enums import WikimediaSite


class Job(BaseModel):
    """A generic job that can be submitted via the API"""

    lang: str = "en"
    site: WikimediaSite = WikimediaSite.wikipedia
    title: str
    testing: bool = False

    def urldecode_title(self):
        """We decode the title to have a human readable string to pass around"""
        self.title = unquote(self.title)
