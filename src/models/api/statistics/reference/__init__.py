from typing import Any, Dict, List

from pydantic import BaseModel

from src.models.api.statistics.reference.template_statistics import TemplateStatistics
from src.models.wikimedia.wikipedia.url import WikipediaUrl


class ReferenceStatistic(BaseModel):
    """The purpose of this class is to model the statistics
    the patron wants from the article endpoint"""

    template_names: List[str] = []
    plain_text_in_reference: bool
    is_named_reference: bool
    wikitext: str
    type: List[str]  # [named|content]
    subtype: List[str]  # [general|citation]
    has_archive_details_url: bool
    has_google_books_url_or_template: bool
    has_web_archive_org_url: bool
    identifiers: Dict[str, Any]  # {dois: [1234,12345], isbns: [1234]}
    flds: List[str]  # first level domain strings
    urls: List[WikipediaUrl] = []
    templates: List[TemplateStatistics]

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
