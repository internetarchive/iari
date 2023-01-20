from pydantic import BaseModel


class CiteWebReferences(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    all: int
    has_google_books_link: int
    has_ia_details_link: int
    has_wm_link: int
    no_link: int
