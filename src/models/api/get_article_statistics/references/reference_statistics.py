from typing import List

from pydantic import BaseModel

from src.models.wikimedia.wikipedia.url import WikipediaUrl


class ReferenceStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_article_statistics endpoint"""

    plain_text_in_reference: bool = False
    citation_template_found: bool = False
    cs1_template_found: bool = False
    citeq_template_found: bool = False
    isbn_template_found: bool = False
    url_template_found: bool = False
    bare_url_template_found: bool = False
    multiple_templates_found: bool = False
    is_named_reference: bool = False
    wikitext: str = ""
    is_citation_reference: bool = False
    is_general_reference: bool = False
    has_archive_details_url: bool = False
    has_google_books_url_or_template: bool = False
    has_web_archive_org_url: bool = False
    url_found: bool = False
    doi: str = ""
    isbn: str = ""
    urls: List[WikipediaUrl] = []
    flds: List[str] = []

    class Config:
        extra = "forbid"
