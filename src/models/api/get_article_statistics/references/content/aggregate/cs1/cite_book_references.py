from pydantic import BaseModel


class CiteBookReferences(BaseModel):
    all: int
    has_url: int
    has_ia_details_url: int
    has_isbn: int
    has_wm_url: int

    class Config:
        extra = "forbid"
