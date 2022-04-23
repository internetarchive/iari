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
        """We hardcode western cultural name ordering pattern here with the order "givenname surname" """
        if self.name_string is None:
            string = ""
            if self.given is not None:
                string += self.given
            if self.surname is not None:
                string += " " + self.surname
        else:
            string = self.name_string
        # We strip spaces to avoid a MWAPIError when a space appears in the beginning of the string
        string = string.lstrip()
        if len(string) > 0:
            return string
        else:
            return None
