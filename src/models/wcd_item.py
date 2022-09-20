from typing import TYPE_CHECKING, Optional

from src.models.wikibase import Wikibase
from src.models.wikibase.wikibase_return import WikibaseReturn
from src.wcd_base_model import WcdBaseModel

if TYPE_CHECKING:
    from src.models.cache import Cache
    from src.models.wikibase.crud.create import WikibaseCrudCreate
    from src.models.wikibase.crud.read import WikibaseCrudRead
    from src.models.wikibase.crud.update import WikibaseCrudUpdate


class WcdItem(WcdBaseModel):
    cache: Optional["Cache"] = None
    language_code: str = "en"
    wikibase_crud_create: Optional["WikibaseCrudCreate"] = None
    wikibase_crud_read: Optional["WikibaseCrudRead"] = None
    wikibase_crud_update: Optional["WikibaseCrudUpdate"] = None
    wikibase_return: Optional[WikibaseReturn] = None
    wikidata_qid: str = ""
    wikibase: Optional[Wikibase] = None

    def __setup_cache__(self):
        from src.models.cache import Cache

        self.cache = Cache()
        self.cache.connect()

    def __setup_wikibase_crud_create__(self):
        from src.models.wikibase.crud.create import WikibaseCrudCreate

        if not self.wikibase_crud_create:
            self.wikibase_crud_create = WikibaseCrudCreate(
                language_code=self.language_code,
                wikibase=self.wikibase,
            )

    def __setup_wikibase_crud_read__(self):
        from src.models.wikibase.crud.read import WikibaseCrudRead

        if not self.wikibase_crud_read:
            self.wikibase_crud_read = WikibaseCrudRead(
                language_code=self.language_code,
                wikibase=self.wikibase,
            )

    def __setup_wikibase_crud_update__(self):
        from src.models.wikibase.crud.update import WikibaseCrudUpdate

        if not self.wikibase_crud_update:
            self.wikibase_crud_update = WikibaseCrudUpdate(
                language_code=self.language_code,
                wikibase=self.wikibase,
            )
        self.wikibase_crud_update.wikipedia_page = self
