from pydantic import BaseModel


class CitationReferences(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    # Reference inside a <ref> tag.
    all: int
