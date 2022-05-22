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
    def full_name(self) -> str:
        """We hardcode western cultural name ordering pattern here with the
        order "givenname surname".  We use str.strip() because no name has
        significant whitespace at the beginning or end of the string

        We want this property to return either the full name or empty string"""
        if self.name_string:
            # Sometimes the reference has a name string with the "full name"
            # so we try that first
            return self.name_string.strip()
        elif self.given or self.surname:
            # First fallback to given name + surname
            return f"{self.given} {self.surname}".strip()
        else:
            # Second fallback
            return ""
