from typing import Optional

from pydantic import BaseModel


class WikipediaPageReference(BaseModel):
    """This models a reference on a Wikipedia page"""
    title: Optional[str] = None
