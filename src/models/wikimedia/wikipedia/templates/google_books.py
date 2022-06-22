"""Template data example: {{google books |plainurl=y |id=CDJpAAAAMAAJ |page=313}}"""
from enum import Enum
from typing import Optional, Union

from marshmallow import Schema, post_load
from marshmallow.fields import String
from pydantic import constr

from src.wcd_base_model import WcdBaseModel


class YesNo(Enum):
    YES = "yes"
    NO = "no"


class YesNoShort(Enum):
    YES = "y"
    NO = "n"


class GoogleBooks(WcdBaseModel):
    id: Optional[constr(max_length=12, min_length=12)]
    keywords: Optional[str]
    page: Optional[int]
    plainurl: Optional[Union[YesNo, YesNoShort]]
    text: Optional[str]
    title: Optional[str]
    first_parameter_id: Optional[constr(max_length=12, min_length=12)]

    @property
    def url(self):
        return f"https://books.google.com/books?id={self.id}"

    def finish_parsing(self):
        if self.first_parameter_id:
            if self.id:
                raise ValueError("Both self.id and self.first_parameter_id specified.")
            else:
                self.id = self.first_parameter_id


class GoogleBooksSchema(Schema):
    """Marshmellow schema to load the attributes using aliases

    We don't validate with marshmellow because it does not seem to work correctly."""

    first_parameter_id = String(data_key="1")  # id
    title = String(data_key="2")  # title

    class Meta:
        additional = ("id", "keywords", "page", "plainurl", "text")

    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs):  # type: ignore
        return GoogleBooks(**data)
