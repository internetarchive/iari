from typing import Optional, Any

from pydantic import BaseModel

from src.models.wikimedia.wikipedia.templates.enums import (
    EnglishWikipediaTemplatePersonRole,
)


class Person(BaseModel):
    """Model a person mentioned in a reference
    Sometimes they are stated as "editor=John Niel"
    and we save that as name_string for later disambiguation"""

    given: Optional[str]
    has_number: bool
    link: Optional[str]
    mask: Optional[str]
    name_string: Optional[str]
    number_in_sequence: Optional[int]
    orcid: Optional[str]
    role: Any
    surname: Optional[str]


class EnglishWikipediaTemplatePerson(Person):
    role: EnglishWikipediaTemplatePersonRole
