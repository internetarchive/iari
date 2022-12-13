import logging
from typing import Dict, Iterable, Optional

from dateutil.parser import isoparse
from pydantic import validate_arguments
from wikibaseintegrator.models import Claim  # type: ignore

from src.wcd_base_model import WcdBaseModel

logger = logging.getLogger(__name__)


class Wikibase(WcdBaseModel):
    """This is a parent class for the wikibases we support
    We define all the properties here to be able to use them in the subclasses"""

    botpassword: str
    item_prefixed_wikibase = True
    query_service_url: str  # we expect a slash in the end
    title: str
    user_name: str
    wikibase_cloud_wikibase: bool = True
    wikibase_url: str  # we expect a slash in the end

    ACCESS_DATE: str  # date
    ARCHIVE: str  # item
    ARCHIVE_DATE: str  # date
    ARCHIVE_URL: str  # url
    AUTHOR: str  # item
    CHAPTER_URL: str
    CITATIONS: str  # item
    CONFERENCE_URL: str
    DOI: str  # external-id
    EDITOR: str  # item
    EDITOR_NAME_STRING: str  # string
    FAMILY_NAME: str  # string
    FIRST_LEVEL_DOMAIN_STRING: str  # string
    FULL_NAME_STRING: str  # string
    FULL_WORK_AVAILABLE_AT_URL: str  # url
    GIVEN_NAME: str  # string
    GOOGLE_BOOKS_ID: str  # external-id
    HASH: str  # string
    HOST_STRING: str  # string
    INSTANCE_OF: str  # item
    INTERNET_ARCHIVE_ID: str  # external-id
    INTERVIEWER_STRING: str  # string
    ISBN_10: str  # external-id
    ISBN_13: str  # external-id
    ISSUE: str  # string
    LAST_UPDATE: str  # date
    LAY_URL: str
    LOCATION_STRING: str  # string
    LUMPED_AUTHORS: str  # string
    MEDIAWIKI_PAGE_ID: str  # string
    NAME_MASK: str  # string
    OCLC_CONTROL_NUMBER: str  # external-id
    ORCID: str  # external-id
    PAGES: str  # string
    PAGE_REVISION_ID: str  # string
    PERIODICAL_STRING: str  # string
    PMID: str  # external-id
    PUBLICATION_DATE: str  # date
    PUBLISHED_IN: str  # ?
    PUBLISHER_STRING: str  # string
    RAW_TEMPLATE: str  # string
    RETRIEVED_DATE: str  # date
    SERIES_ORDINAL: str  # aka author position # quantity
    SOURCE_WIKIPEDIA: str  # item
    STRING_CITATIONS: str  # string
    TEMPLATE_NAME: str  # string
    TITLE: str  # monolingual text
    TRANSCRIPT_URL: str
    TRANSLATOR_NAME_STRING: str  # string
    URL: str  # url
    VOLUME: str  # string
    WEBSITE: str  # item
    WEBSITE_STRING: str  # string
    WIKIDATA_QID: str  # external id

    ENGLISH_WIKIPEDIA: str = (
        ""  # label: English Wikipedia description: language version of Wikipedia
    )
    WEBSITE_ITEM: str = (
        ""  # label: Website description: first level domain website found in Wikipedia
    )
    WIKIPEDIA_PAGE: str = (
        ""  # label: Wikipedia page description: page in a language version of Wikipedia
    )
    WIKIPEDIA_REFERENCE: str = (
        ""  # label: Wikipedia reference description: reference on a page in Wikipedia
    )
    ARCHIVE_ITEM: str = ""  # label: Archive description: web archive
    ARCHIVE_IS: str = ""  # label: Archive.is description: web archive
    ARCHIVE_ORG: str = ""  # label: Archive.org description: web archive
    ARCHIVE_TODAY: str = ""  # label: Archive.today description: web archive
    WEBCITATION_ORG: str = ""  # label: Webcitation.org description: web archive
    GHOSTARCHIVE_ORG: str = ""

    # This must come last to avoid errors
    wcdqid_language_edition_of_wikipedia_to_work_on: str = ""

    @property
    def mediawiki_api_url(self) -> str:
        return self.wikibase_url + "w/api.php"

    @property
    def mediawiki_index_url(self) -> str:
        return self.wikibase_url + "w/index.php"

    @property
    def rdf_entity_prefix_url(self) -> str:
        return self.rdf_prefix_url + "entity/"

    @property
    def rdf_prefix_prop_direct_url(self) -> str:
        """This is the truthy property url"""
        return self.rdf_prefix_url + "prop/direct/"

    @property
    def rdf_prefix_url(self) -> str:
        """We only support wikibase.cloud Wikibase installations for now"""
        return self.wikibase_url

    @property
    def sparql_endpoint_url(self) -> str:
        if self.wikibase_cloud_wikibase:
            """This is the default endpoint url for Wikibase.cloud instances"""
            return self.wikibase_url + "query/sparql"
        else:
            """This is the default docker Wikibase endpoint url
            Thanks to @Myst for finding/documenting it."""
            return self.query_service_url + "proxy/wdqs/bigdata/namespace/wdq/sparql"

    @validate_arguments
    def entity_history_url(self, item_id: str):
        if self.item_prefixed_wikibase:
            return f"{self.wikibase_url}w/index.php?title=Item:{item_id}&action=history"
        else:
            return f"{self.wikibase_url}w/index.php?title={item_id}&action=history"

    @validate_arguments
    def entity_url(self, item_id: str):
        if self.item_prefixed_wikibase:
            return f"{self.wikibase_url}wiki/Item:{item_id}"
        else:
            return f"{self.wikibase_url}wiki/{item_id}"

    @staticmethod
    def parse_time_from_claim(claim: Claim):
        return isoparse(
            claim.mainsnak.datavalue["value"]["time"].replace("+", "")
        )  # .astimezone(timezone.utc)

    @validate_arguments
    def is_valid_qid(self, qid: str) -> bool:
        """Validate the qid"""
        if qid[:1].upper() == "Q" and qid[1:].isnumeric():
            return True
        else:
            return False

    # TODO the following 2 methods are redundant and should be removed
    #  they are only here because we integrated wikicitations-api quickly
    @validate_arguments
    def extract_item_ids(self, sparql_result: Optional[Dict]) -> Iterable[str]:
        """Yield item ids from a sparql result"""
        if sparql_result:
            yielded = 0
            for binding in sparql_result["results"]["bindings"]:
                if item_id := self.__extract_wcdqs_json_entity_id__(data=binding):
                    yielded += 1
                    yield item_id
            if number_of_bindings := len(sparql_result["results"]["bindings"]):
                logger.info(f"Yielded {yielded} bindings out of {number_of_bindings}")

    @validate_arguments
    def __extract_wcdqs_json_entity_id__(
        self, data: Dict, sparql_variable: str = "item"
    ) -> str:
        """We default to "item" as sparql value because it is customary in the Wikibase ecosystem"""
        return str(
            data[sparql_variable]["value"].replace(self.rdf_entity_prefix_url, "")
        )

    @property
    def wcd_prefix_line(self):
        return f"prefix wcd: <{self.rdf_entity_prefix_url}>"

    @property
    def wcdt_prefix_line(self):
        return f"prefix wcdt: <{self.rdf_prefix_prop_direct_url}>"

    @property
    def prefix_lines(self):
        return f"{self.wcd_prefix_line}\n{self.wcdt_prefix_line}"
