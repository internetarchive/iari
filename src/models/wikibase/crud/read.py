import logging
from typing import Any, Dict, List, Optional

from pydantic import validate_arguments
from wikibaseintegrator import WikibaseIntegrator  # type: ignore
from wikibaseintegrator.entities import ItemEntity  # type: ignore
from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore

from src.models.exceptions import MissingInformationError
from src.models.wikibase.crud import WikibaseCrud

logger = logging.getLogger(__name__)


class WikibaseCrudRead(WikibaseCrud):
    # TODO refactor these get all functions
    @validate_arguments
    def __get_all_items__(self, item_type):
        pass

    def __get_all_page_items__(self):
        """Get all wcdqids for wikipedia pages using sparql"""
        if not self.wikibase.INSTANCE_OF:
            raise MissingInformationError("self.wikibase.INSTANCE_OF was empty string")
        return self.__extract_item_ids__(
            sparql_result=self.__get_items_via_sparql__(
                f"""
            prefix wcd: <{self.wikibase.rdf_prefix}/entity/>
            prefix wcdt: <{self.wikibase.rdf_prefix}/prop/direct/>
            SELECT ?item WHERE {{
              ?item wcdt:{self.wikibase.INSTANCE_OF} wcd:{self.wikibase.WIKIPEDIA_PAGE}
            }}
            """
            )
        )

    def __get_all_reference_items__(self):
        """Get all wcdqids for references using sparql"""
        if not self.wikibase.INSTANCE_OF:
            raise MissingInformationError("self.wikibase.INSTANCE_OF was empty string")
        return self.__extract_item_ids__(
            sparql_result=self.__get_items_via_sparql__(
                f"""
            prefix wcd: <{self.wikibase.rdf_prefix}/entity/>
            prefix wcdt: <{self.wikibase.rdf_prefix}/prop/direct/>
            SELECT ?item WHERE {{
                ?item wcdt:{self.wikibase.INSTANCE_OF} wcd:{self.wikibase.WIKIPEDIA_REFERENCE}
            }}
            """
            )
        )

    def __get_all_website_items__(self):
        """Get all wcdqids for website items using sparql"""
        if not self.wikibase.INSTANCE_OF:
            raise MissingInformationError("self.wikibase.INSTANCE_OF was empty string")
        return self.__extract_item_ids__(
            sparql_result=self.__get_items_via_sparql__(
                f"""
            prefix wcd: <{self.wikibase.rdf_prefix}/entity/>
            prefix wcdt: <{self.wikibase.rdf_prefix}/prop/direct/>
            SELECT ?item WHERE {{
                ?item wcdt:{self.wikibase.INSTANCE_OF} wcd:{self.wikibase.WEBSITE}
            }}
            """
            )
        )

    @validate_arguments
    def __get_item_entity_from_wcdqs_json__(
        self, data: Dict, sparql_variable: str = "item"
    ) -> ItemEntity:
        return self.__convert_wcd_entity_id_to_item_entity__(
            self.__extract_wcdqs_json_entity_id__(
                data=data, sparql_variable=sparql_variable
            )
        )

    @validate_arguments
    def __get_items_via_sparql__(self, query: str) -> Any:
        """This is the lowest level function
        that executes the query with WBI after setting it up"""
        self.__setup_wikibase_integrator_configuration__()
        self.__wait_for_wcdqs_to_sync__()
        logger.debug(
            f"Trying to use this endpoint: {self.wikibase.sparql_endpoint_url}"
        )
        return execute_sparql_query(
            query=query, endpoint=self.wikibase.sparql_endpoint_url
        )

    @validate_arguments
    def __get_wcdqids_from_hash__(self, md5hash: str) -> List[str]:
        """This is a slower SPARQL-powered fallback helper method
        used when config.use_cache is False"""
        logger.debug("__get_wcdqid_from_hash__: running")
        if not self.wikibase.HASH:
            raise MissingInformationError("self.wikibase.HASH was empty string")
        query = f"""
            prefix wcdt: <{self.wikibase.rdf_prefix}/prop/direct/>
            SELECT ?item WHERE {{
              ?item wcdt:{self.wikibase.HASH} "{md5hash}".
            }}
        """
        return list(
            self.__extract_item_ids__(
                sparql_result=self.__get_items_via_sparql__(query=query)
            )
        )

    @validate_arguments
    def get_item(self, item_id: str) -> Optional[ItemEntity]:
        """Get one item from WikiCitations"""
        self.__setup_wikibase_integrator_configuration__()
        wbi = WikibaseIntegrator()
        return wbi.item.get(item_id)
