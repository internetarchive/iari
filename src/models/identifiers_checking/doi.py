from typing import Any, Dict, List, Optional
from urllib.parse import quote

import pyalex  # type: ignore
import requests
from pyalex import Works  # type: ignore
from pydantic import BaseModel
from wikibaseintegrator import WikibaseIntegrator  # type: ignore
from wikibaseintegrator.entities import ItemEntity  # type: ignore
from wikibaseintegrator.models import Claim  # type: ignore
from wikibaseintegrator.wbi_config import config  # type: ignore
from wikibaseintegrator.wbi_helpers import fulltext_search  # type: ignore

instance_of = "P31"
retracted_item = "Q45182324"  # see https://www.wikidata.org/wiki/Q45182324
pyalex.config.email = "info@archive.org"
config["USER_AGENT"] = "wcdimportbot"


class Doi(BaseModel):
    """This models a DOI and contains logic to look it up
    We use BaseModel because we want to expose it in the get-statistics API"""

    wikidata: Dict[str, Any] = {}
    openalex: Dict[str, Any] = {}
    fatcat: Dict[str, Any] = {}
    doi: str
    found_in_wikidata: bool = False
    found_in_openalex: bool = False
    wikidata_entity: Optional[ItemEntity]
    marked_as_retracted_in_wikidata: bool = False
    marked_as_retracted_in_openalex: bool = False
    wikidata_entity_qid: str = ""
    openalex_work_uri: str = ""
    wbi = WikibaseIntegrator()
    timeout: int = 2
    internet_archive_scholar: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True

    @property
    def wikidata_entity_uri(self):
        return f"http://www.wikidata.org/entity/{self.wikidata_entity_qid}"

    def lookup_doi(self):
        """Helper method"""
        from src.models.api import app

        app.logger.debug("lookup_doi: running")
        self.__lookup_doi_in_openalex__()
        self.__lookup_via_cirrussearch__()
        self.__lookup_in_internet_archive_scholar__()
        self.__analyze_wikidata_entity__()
        self.__get_wikidata_json__()
        self.__log_if_retracted_or_not__()
        self.__lookup_in_fatcat__()

    def __lookup_doi_in_openalex__(self):
        from src.models.api import app

        app.logger.info("Looking up DOI in OpenAlex")
        work = Works()[f"https://doi.org/{self.doi}"]
        if work:
            app.logger.debug("found work :)")
            self.found_in_openalex = True
            self.marked_as_retracted_in_openalex = bool(work["is_retracted"])
            self.openalex = dict(
                id=work["id"],
                details=work,
                retracted=self.marked_as_retracted_in_openalex,
            )
            app.logger.info(
                f"Retracted in OpenAlex: {self.marked_as_retracted_in_openalex}"
            )

    def __get_wikidata_entity__(self):
        from src.models.api import app

        app.logger.debug("__get_wikidata_entity__: running")
        if self.found_in_wikidata:
            self.wikidata_entity = self.wbi.item.get(
                entity_id=self.wikidata_entity_qid.replace(
                    "https://www.wikidata.org/wiki/", ""
                )
            )

    def __analyze_wikidata_entity__(self):
        """Helper method"""
        self.__get_wikidata_entity__()
        self.__determine_if_retracted_in_wikidata__()
        # self.count_cites_work_statements()
        # self.get_count_of_all_statements()

    def __determine_if_retracted_in_wikidata__(self):
        from src.models.api import app

        if self.wikidata_entity:
            instance_of_claims = self.wikidata_entity.claims.get(property=instance_of)
            app.logger.debug(f"Found {len(instance_of_claims)} instance of claims")
            # console.print(instance_of_claims)
            self.__iterate_claims__(claims=instance_of_claims)

    def __lookup_via_cirrussearch__(self) -> None:
        from src.models.api import app

        entities = fulltext_search(
            search=f"haswbstatement:P356={self.doi}", max_results=1
        )
        if entities:
            # We only care about the first because there should only be one
            self.wikidata_entity_qid = entities[0]["title"]
            self.found_in_wikidata = True
            app.logger.info("DOI found via CirrusSearch")
        else:
            self.found_in_wikidata = False
            app.logger.info("DOI not found via CirrusSearch")

    def __determine_if_retracted__(self, claim: Claim) -> None:
        from src.models.api import app

        app.logger.debug("__determine_if_retracted__: running")
        # console.print(claim)
        datavalue = claim.mainsnak.datavalue
        # print(datavalue)
        value = datavalue["value"]
        if isinstance(value, dict) and "id" in value.keys():
            qid_value = value["id"]
            app.logger.debug(f"found P31: '{qid_value}'")
            if qid_value == retracted_item:
                self.marked_as_retracted_in_wikidata = True
                app.logger.info("This paper is marked as retracted in Wikidata")

    def __iterate_claims__(self, claims: List[Claim]) -> None:
        for claim in claims:
            self.__determine_if_retracted__(claim=claim)

    def __log_if_retracted_or_not__(self):
        from src.models.api import app

        if self.found_in_openalex and self.found_in_wikidata:
            if (
                self.marked_as_retracted_in_openalex
                and not self.marked_as_retracted_in_wikidata
            ):
                app.logger.info(
                    f"This paper is marked retracted in OpenAlex, "
                    f"but is missing P31:{retracted_item} in Wikidata, see {self.wikidata_entity_uri}"
                )
            elif (
                not self.marked_as_retracted_in_openalex
                and self.marked_as_retracted_in_wikidata
            ):
                app.logger.info(
                    f"This paper is marked retracted in Wikidata, "
                    f"but not in OpenAlex, see {self.openalex_work_uri}"
                )
            elif (
                self.marked_as_retracted_in_openalex
                and self.marked_as_retracted_in_wikidata
            ):
                app.logger.info(
                    f"This paper is marked retracted in both Wikidata and OpenAlex"
                )
            elif (
                not self.marked_as_retracted_in_openalex
                and not self.marked_as_retracted_in_wikidata
            ):
                app.logger.info(
                    f"This paper is not marked retracted in any of the catalog sources we support."
                )
        else:
            app.logger.info("This paper was not found in both OpenAlex and Wikidata")

    def get_doi_dictionary(self) -> Dict[str, Any]:
        data = self.dict(
            include={
                "wikidata",
                "openalex",
                "timeout",
                "doi",
                "fatcat",
                "internet_archive_scholar",
            }
        )
        return data

    def __lookup_in_fatcat__(self):
        """DOIs in fatcat are all lowercase"""
        url = f"https://api.fatcat.wiki/v0/release/lookup?doi={self.doi.lower()}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            self.fatcat["id"] = data["ident"]
            self.fatcat["details"] = data
            # console.print(self.fatcat)

    def __get_wikidata_json__(self):
        if self.found_in_wikidata and self.wikidata_entity:
            self.wikidata = dict(
                details=self.wikidata_entity.get_json(),
                id=self.wikidata_entity.id,
                retracted=self.marked_as_retracted_in_wikidata,
            )

    def __lookup_in_internet_archive_scholar__(self):
        """This is a fastapi frontend to elastic search"""
        query = f"doi{quote(':')}{quote(self.doi, safe='')}"
        url = f"https://scholar.archive.org/search?q={query}"
        response = requests.get(url, headers=dict(Accept="application/json"))
        if response.status_code == 200:
            data = response.json()
            self.internet_archive_scholar = data
