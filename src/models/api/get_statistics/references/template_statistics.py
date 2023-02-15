from typing import Optional

from pydantic import BaseModel

from src.models.identifiers.doi import Doi


class TemplateStatistics(BaseModel):
    """The purpose of this class is to model the get_statistics
    the user wants from the get_article_statistics endpoint"""

    is_isbn_template: bool
    is_bareurl_template: bool
    is_citeq_template: bool
    is_citation_template: bool
    is_cs1_template: bool
    is_url_template: bool
    is_webarchive_template: bool
    is_known_multiref_template: bool
    doi: str
    isbn: str
    wikitext: str
    doi_details: Optional[Doi]

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
