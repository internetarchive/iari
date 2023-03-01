from typing import Optional

from src.wcd_base_model import WcdBaseModel

# if TYPE_CHECKING:
#     from src.models.wikibase.crud.create import WikibaseCrudCreate
#     from src.models.wikibase.crud.read import WikibaseCrudRead


class WcdItem(WcdBaseModel):
    language_code: str = "en"
    # wikibase_crud_create: Optional["WikibaseCrudCreate"] = None
    # wikibase_crud_read: Optional["WikibaseCrudRead"] = None
    # return_: Optional[Return] = None
    wikidata_qid: str = ""
    # wikibase: Optional[Wikibase] = None
    title: str = ""

    # def __setup_wikibase_crud_create__(self):
    #     from src.models.wikibase.crud.create import WikibaseCrudCreate
    #
    #     if not self.wikibase_crud_create:
    #         self.wikibase_crud_create = WikibaseCrudCreate(
    #             language_code=self.language_code,
    #             wikibase=self.wikibase,
    #         )
    #
    # def __setup_wikibase_crud_read__(self):
    #     from src.models.wikibase.crud.read import WikibaseCrudRead
    #
    #     if not self.wikibase_crud_read:
    #         self.wikibase_crud_read = WikibaseCrudRead(
    #             language_code=self.language_code,
    #             wikibase=self.wikibase,
    #         )
