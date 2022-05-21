from typing import Optional, Any

from pydantic import BaseModel


class Person(BaseModel):
    """Model a person mentioned in a page_reference
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

    @property
    def author_name_string(self) -> Optional[str]:
        """We hardcode western cultural name ordering pattern here with the
        order "givenname surname".  We use str.strip() because no name has
        significant whitespace at the beginning or end of the string"""
        return (
            (self.name_string or "").strip()
            or f"{self.given or ''} {self.surname or ''}".strip()
            or None
        )
