import logging
from typing import Union

from flask import redirect
from flask_restful import Resource  # type: ignore

import config
from src.models.api.enums import Return
from src.models.api.lookup_wikicitations_qid import LookupWikicitationsQid

logger = logging.getLogger(__name__)


class LookupByWikidataQid(Resource):
    @staticmethod
    def get(qid=""):
        if qid:
            if config.use_sandbox_wikibase_backend_for_wikicitations_api:
                from src import IASandboxWikibase

                wikibase = IASandboxWikibase()
            else:
                from src import WikiCitationsWikibase

                wikibase = WikiCitationsWikibase()
            logger.info(f"Got QID, looking up now in {wikibase.__repr_name__()}")
            lwq = LookupWikicitationsQid()
            result: Union[Return, str] = lwq.lookup_via_query_service(wdqid=qid)
            if isinstance(result, str):
                return redirect(wikibase.entity_url(item_id=result))
            elif result == Return.NO_MATCH:
                # https://www.geeksforgeeks.org/string-formatting-in-python/
                return result.value.format(wikibase=wikibase.__repr_name__(), qid=qid), 404
            else:
                return result.value, 400
        else:
            return Return.NO_QID.value, 400
