from typing import Optional

from wikibaseintegrator.entities import ItemEntity  # type: ignore

from src.models.return_ import Return


class WikibaseReturn(Return):
    item: Optional[ItemEntity]

    class Config:
        arbitrary_types_allowed = True
