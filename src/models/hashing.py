import hashlib

from src.models.wikibase import Wikibase
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.enums import WikimediaSite
from src.wcd_base_model import WcdBaseModel


class Hashing(WcdBaseModel):
    wikibase: Wikibase = IASandboxWikibase()
    language_code: str = "en"
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    title: str = ""
    article_wikidata_qid: str = ""

    def __entity_updated_hash_key__(
        self,
    ) -> str:
        """Key we use to lookup the timestamp in SSDB

        We encode the information we need to make it
        unique and quick to lookup of the timestamp"""
        if self.title:
            title_or_wdqid = self.title
        else:
            title_or_wdqid = self.article_wikidata_qid
        return hashlib.md5(
            f"{self.wikibase.title}-"
            f"{title_or_wdqid}-"
            f"{self.language_code}-"
            f"{self.wikimedia_site.value}-"
            f"updated".encode()
        ).hexdigest()
