from typing import TYPE_CHECKING, Optional, Any

from src.models.return_ import Return
from src.models.wikibase import Wikibase
from src.wcd_base_model import WcdBaseModel

if TYPE_CHECKING:
    # from src.models.cache import Cache
    from src.models.wikibase.crud.create import WikibaseCrudCreate
    from src.models.wikibase.crud.read import WikibaseCrudRead
    from src.models.wikibase.crud.update import WikibaseCrudUpdate


class WcdItem(WcdBaseModel):
    # We set to Any here because of cyclic dependency or pydantic forward ref error
    cache: Optional[Any] = None
    language_code: str = "en"
    wikibase_crud_create: Optional["WikibaseCrudCreate"] = None
    wikibase_crud_read: Optional["WikibaseCrudRead"] = None
    wikibase_crud_update: Optional["WikibaseCrudUpdate"] = None
    return_: Optional[Return] = None
    wikidata_qid: str = ""
    wikibase: Optional[Wikibase] = None
    title: str = ""

    def __setup_cache__(self):
        from src.models.cache import Cache
        if not self.cache:
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

    def __setup_wikibase_crud_update__(self, wikipedia_article: "WcdItem"):
        from src.models.wikibase.crud.update import WikibaseCrudUpdate

        if not self.wikibase_crud_update:
            self.wikibase_crud_update = WikibaseCrudUpdate(
                language_code=self.language_code,
                wikibase=self.wikibase,
            )
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        if not isinstance(wikipedia_article, WikipediaArticle):
            raise TypeError("not a WikipediaArticle")
        self.wikibase_crud_update.wikipedia_article = wikipedia_article
