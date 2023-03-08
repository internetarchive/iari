from typing import Any, Dict, List

from pydantic import BaseModel

from src.models.wikimedia.wikipedia.reference.template.person import Person


class TemplateStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the patron wants from the article endpoint"""

    name: str
    wikitext: str
    # The title is in the dictionary also
    parameters: Dict[str, Any] = {}  # {isbn: "1234", doi: "1234"}
    persons: List[Person] = []

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
