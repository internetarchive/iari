import hashlib

from src import MissingInformationError
from src.models.wikibase import Wikibase
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.enums import WikimediaSite
from src.wcd_base_model import WcdBaseModel


class Hashing(WcdBaseModel):
    """Here we handle all the neccesary hashing"""
    wikibase: Wikibase = IASandboxWikibase()
    language_code: str = "en"
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    title: str = ""
    article_wikidata_qid: str = ""
    raw_template: str = ""
    testing: bool = False

    def __generate_entity_updated_hash_key__(
        self,
    ) -> str:
        """Key we use to lookup the timestamp in SSDB

        We encode the information we need to make it
        unique and quick to lookup of the timestamp"""
        if not self.title and not self.article_wikidata_qid:
            if not self.testing:
                raise MissingInformationError("self.title and self.article_wikidata_qid was empty")
            else:
                # generate a nonsense hash to avoid test failure
                return hashlib.md5(
                    f"testing-"
                    f"updated".encode()
                ).hexdigest()
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

    def generate_raw_reference_hash(self):
        """Calculate the md5 hash used in the title of the wikipage"""
        if not self.raw_template:
            raise MissingInformationError("self.raw_template was empty")
        # We lower case the whole thing first because we don't care about casing
        return hashlib.md5(
            f"{self.raw_template.lower()}".encode()
        ).hexdigest()