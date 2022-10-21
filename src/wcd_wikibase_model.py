from src import WcdBaseModel
from src.models.wikibase import Wikibase
from src.models.wikibase.enums import SupportedWikibase
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikibase.wikicitations_wikibase import WikiCitationsWikibase


class WcdWikibaseModel(WcdBaseModel):
    target_wikibase: SupportedWikibase = SupportedWikibase.IASandboxWikibase
    wikibase: Wikibase


    def setup_wikibase(self):
        if self.target_wikibase == SupportedWikibase.IASandboxWikibase:
            self.wikibase = IASandboxWikibase()
        elif self.target_wikibase == SupportedWikibase.IASandboxWikibase:
            self.wikibase = WikiCitationsWikibase()
        else:
            raise Exception("target_wikibase error")

