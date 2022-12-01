import logging
from typing import Optional, Union

from pydantic import BaseModel
from wikibaseintegrator import wbi_config  # type: ignore
from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore

import config
from src.helpers.console import console
from src.models.api.enums import Return
from src.models.exceptions import NotSupportedError
from src.models.wikibase import Wikibase

logger = logging.getLogger(__name__)


class LookupWikicitationsQid(BaseModel):
    """lookup the wcdqid based on the wdqid"""

    wikibase: Optional[Wikibase]

    def __setup_wikibase_integrator_configuration__(self) -> None:
        if config.use_sandbox_wikibase_backend_for_wikicitations_api:
            from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase

            self.wikibase = IASandboxWikibase()
        else:
            from src.models.wikibase.wikicitations_wikibase import WikiCitationsWikibase

            self.wikibase = WikiCitationsWikibase()
        wbi_config.config["USER_AGENT"] = config.user_agent
        wbi_config.config["WIKIBASE_URL"] = self.wikibase.wikibase_url
        wbi_config.config["MEDIAWIKI_API_URL"] = self.wikibase.mediawiki_api_url
        wbi_config.config["MEDIAWIKI_INDEX_URL"] = self.wikibase.mediawiki_index_url
        wbi_config.config["SPARQL_ENDPOINT_URL"] = self.wikibase.sparql_endpoint_url

    def lookup_via_query_service(self, wdqid="") -> Union[Return, str]:
        """This looks up the WDQID via the query service. It is way
        slower than using cirrussearch, but cirrussearch is currently
        not installed on the wikibases we support"""
        if wdqid:
            self.__setup_wikibase_integrator_configuration__()
            if not self.wikibase:
                raise ValueError("self.wikibase was None")
            if self.wikibase.is_valid_qid(qid=wdqid):
                wikibase_property = self.wikibase.WIKIDATA_QID
                # We uppercase the QID because the SPARQL string matching is probably case-sensitive
                query = f"""
                {self.wikibase.prefix_lines}
                    SELECT ?item WHERE {{
                      ?item wcdt:{wikibase_property} "{wdqid.upper()}".
                    }}
                """
                result = execute_sparql_query(query=query)
                if config.loglevel == logging.DEBUG:
                    console.print(result)
                wcdqids = self.wikibase.extract_item_ids(sparql_result=result)
                # logger.info(f"Found {wcdqids}")
                for wcdqid in wcdqids:
                    # We only ever care about the first
                    return wcdqid
                return Return.NO_MATCH
            else:
                return Return.INVALID_QID
        else:
            return Return.NO_QID

    def lookup_via_cirrussearch(self, wdqid=""):
        """This does not work because the WikibaseCirrusSearch
        extension is not enabled yet on our Wikibases in Wikibase.cloud"""
        raise NotSupportedError(
            "This does not work because the WikibaseCirrusSearch "
            "extension is not enabled yet on our Wikibases in Wikibase.cloud"
        )
        # self.__setup_wikibase_integrator_configuration__()
        # wbi = WikibaseIntegrator()
        # data = {
        #     'action': 'query',
        #     'list': 'search',
        #     'srsearch': f'haswbstatement:{config.wikidata_qid_property}={wdqid}',
        # }
        # result = wbi_helpers.mediawiki_api_call_helper(data=data, allow_anonymous=True, user_agent=config.user_agent)
        # #console.print(result)
        # #console.print(result.get("query"))
        # if result.get("query"):
        #     logger.debug("got query")
        #     if result.get("query").get("searchinfo"):
        #         logger.debug("got searchinfo")
        #         totalhits = int(result.get("query").get("searchinfo").get("totalhits"))
        #         if totalhits:
        #             logger.debug("got totalhits > 0")
        #             first_hit = result.get("query").get("search")[0]
        #             console.print(first_hit)
        #             return first_hit
        #         else:
        #             message = "No hit for this qid in Wikicitations"
        #             logger.info(message)
        #             return message
