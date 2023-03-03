from typing import Any, Dict, List

from pydantic import BaseModel

from src.models.api.statistics.reference.template_statistics import TemplateStatistics


class ReferenceStatistic(BaseModel):
    """The purpose of this class is to model the statistics
    the patron wants from the article endpoint"""

    id: str = ""
    template_names: List[str] = []
    wikitext: str
    type: str  # # [general|footnote]
    footnote_subtype: str = ""  # [named|content]
    # identifiers: Dict[str, Any]  # {dois: [1234,12345], isbns: [1234]}
    flds: List[str] = []  # non-unique first level domain strings
    urls: List[str] = []  # non-unique url strings
    templates: List[Dict[str, Any]] = []
    titles: List[str] = []

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
