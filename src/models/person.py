from typing import Optional

from pydantic import BaseModel

from src.models.enums import Role


class Person(BaseModel):
    """Model a person mentioned in a reference
    Sometimes they are stated as "editor=John Niel"
    and we save that as name_string for later disambiguation"""

    given: Optional[str]
    surname: Optional[str]
    name_string: Optional[str]
    mask: Optional[str]
    orcid: Optional[str]
    link: Optional[str]
    role: Role
    number_in_sequence: Optional[int]
    has_number: bool
