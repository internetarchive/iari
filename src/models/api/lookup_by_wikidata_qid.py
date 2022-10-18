from typing import Union

from flask_restful import Resource # type: ignore

from src.models.api.enums import Return
from src.models.api.lookup_wikicitations_qid import LookupWikicitationsQid


class LookupByWikidataQid(Resource):
    @staticmethod
    def get(qid=""):
        if qid:
            lwq = LookupWikicitationsQid()
            result: Union[Return, str] = lwq.lookup_via_query_service(wdqid=qid)
            if isinstance(result, str):
                return result, 200
            elif result == Return.NO_MATCH:
                return result.value, 404
            else:
                return result.value, 400
        else:
            return Return.NO_QID.value, 400
