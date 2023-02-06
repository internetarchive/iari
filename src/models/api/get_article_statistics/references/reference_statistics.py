from typing import List

from pydantic import BaseModel

from src.models.api.get_article_statistics.references.template_statistics import (
    TemplateStatistics,
)
from src.models.wikimedia.wikipedia.url import WikipediaUrl


class ReferenceStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_article_statistics endpoint"""

    plain_text_in_reference: bool
    citation_template_found: bool
    cs1_template_found: bool
    citeq_template_found: bool
    isbn_template_found: bool
    url_template_found: bool
    bare_url_template_found: bool
    multiple_templates_found: bool
    is_named_reference: bool
    wikitext: str
    is_citation_reference: bool
    is_general_reference: bool
    has_archive_details_url: bool
    has_google_books_url_or_template: bool
    has_web_archive_org_url: bool
    url_found: bool
    # todo convert these to list of string
    doi: str
    isbn: str
    multiple_cs1_templates_found: bool
    known_multiref_template_found: bool
    number_of_bareurl_templates: int
    number_of_citation_templates: int
    number_of_citeq_templates: int
    number_of_cs1_templates: int
    number_of_isbn_templates: int
    number_of_templates: int
    number_of_templates_missing_first_parameter: int
    number_of_url_templates: int
    number_of_webarchive_templates: int
    is_valid_qid: bool
    wikidata_qid: str
    urls: List[WikipediaUrl] = []
    flds: List[str] = []
    templates: List[TemplateStatistics]

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
