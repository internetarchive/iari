from typing import Any, Dict, List

from pydantic import BaseModel


class ReferenceStatisticsV2(BaseModel):
    """
    provides the properties returned for reference objects
    """

    id: str = ""
    ref_index: int = 0
    name: str = ""
    type: str  # [general|footnote]
    footnote_subtype: str  # [named|content]
    section: str = ""

    titles: List[str] = []
    template_names: List[str]
    templates: List[Dict[str, Any]]
    urls: List[str] = []  # non-unique url strings
    url_objects: List[Dict[str, Any]]
    flds: List[str] = []  # non-unique first level domain strings

    wikitext: str
    # identifiers: Dict[str, Any]  # {dois: [1234,12345], isbns: [1234]}

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
