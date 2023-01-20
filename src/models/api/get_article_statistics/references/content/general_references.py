from pydantic import BaseModel


class GeneralReferences(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    # References outside a <ref> tag e.g. in a bibliography section
    all: int
