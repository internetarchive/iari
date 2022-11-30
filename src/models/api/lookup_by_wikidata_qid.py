import logging
from typing import Union

from flask import redirect
from flask_restful import Resource  # type: ignore

from src.models.api.enums import Return
from src.models.api.lookup_wikicitations_qid import LookupWikicitationsQid

logger = logging.getLogger(__name__)


class LookupByWikidataQid(Resource):
    @staticmethod
    def get(qid=""):
        if qid:
            logger.info("Got QID, looking up now")
            lwq = LookupWikicitationsQid()
            result: Union[Return, str] = lwq.lookup_via_query_service(wdqid=qid)
            if isinstance(result, str):
                from src import WikiCitationsWikibase

                wikibase = WikiCitationsWikibase()
                return redirect(wikibase.entity_url(item_id=result))
            elif result == Return.NO_MATCH:
                return result.value, 404
            else:
                return result.value, 400
        else:
            return Return.NO_QID.value, 400
