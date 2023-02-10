from pydantic import BaseModel

from src.models.api.get_statistics.references.content import ContentReferences


class ReferenceTypes(BaseModel):
    """The purpose of this class is to model the get_statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    # Reference with content
    content: ContentReferences
    # Type of reference which does not have any content and only refer to another <ref> using a name
    named: int

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
