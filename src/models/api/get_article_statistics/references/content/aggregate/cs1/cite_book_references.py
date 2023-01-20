from pydantic import BaseModel


class CiteBookReferences(BaseModel):
    all: int
    has_wm_link: int
    has_ia_details_link: int
    no_link: int
    has_isbn: int
