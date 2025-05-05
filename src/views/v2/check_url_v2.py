import hashlib
import logging
import traceback

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.models.exceptions import MissingInformationError
# from src.models.file_io.url_file_io import UrlFileIo
from src.models.v2.file_io.check_url_file_io_v2 import CheckUrlFileIoV2
from src.views.v2.statistics import StatisticsViewV2

from src.constants.constants import CheckMethod

from src.models.v2.job.check_url_job_v2 import CheckUrlJobV2
from src.models.v2.schema.check_url_schema_v2 import CheckUrlSchemaV2

# from src.models.identifiers_checking.url import Url

# ???
# ???
from src.models.identifiers_checking.url import Url
# ???
# ???



logger = logging.getLogger(__name__)


class CheckUrlV2(StatisticsViewV2):
    """
    This view does not contain any of the checking logic.
    See src/models/checking
    """

    job: Optional[CheckUrlJobV2] = None
    schema: Schema = CheckUrlSchemaV2()

    # ### serving_from_json: bool = False
    headers: Optional[Dict[str, Any]] = None
    #     {
    #     "Access-Control-Allow-Origin": "*",
    # }
    data: Optional[Dict[str, Any]] = None

    @property
    def __url_hash_id__(self) -> str:
        """Generates an 8-char id based on md5 hash of the raw upper-cased URL """
        if not self.job:
            raise MissingInformationError()

        return hashlib.md5(f"{self.job.unquoted_url.upper()}".encode()).hexdigest()[:8]

    def get(self):
        """main method of the check-url entrypoint for flask
        must return a tuple (Any,response_code)"""
        from src import app

        app.logger.debug("CheckUrlV2: running")
        try:
            self.__validate_and_get_job__()
            if self.job:
                return self.__return_from_cache_or_analyze_and_return__()

        except MissingInformationError as e:
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500


    def __setup_io__(self):
        logger.debug(
            f"CheckUrlV2:__setup_io__: self._url_hash_id = {self.__url_hash_id__}"
        )
        self.io = CheckUrlFileIoV2(
            hash_based_id=self.__url_hash_id__,
            file_prefix=self.job.method,
        )

    def __return_from_cache_or_analyze_and_return__(self):
        if not self.job.refresh:
            self.__setup_and_read_from_cache__()
            if self.io.data:
                return self.io.data, 200
            else:
                return self.__return_fresh_data__()
        else:
            return self.__return_fresh_data__()

    def __return_fresh_data__(self):
        from src import app

        url_string = self.job.unquoted_url
        app.logger.info(f"CheckUrlV2::__return_fresh_data__: url is {url_string}")
        url = Url(url=url_string, timeout=self.job.timeout)

        url.check(self.job.method)

        data = url.get_dict

        timestamp = datetime.timestamp(datetime.utcnow())
        isodate = datetime.isoformat(datetime.utcnow())
        url_hash_id = self.__url_hash_id__

        data["timestamp"] = int(timestamp)
        data["isodate"] = str(isodate)
        data["id"] = url_hash_id

        data_without_text = deepcopy(data)
        del data_without_text["text"]
        # TODO re-do this include text logic - send flag to include text or not
        #   maybe make an "options" to url.check() so that only extras we want are calculated

        self.__write_to_cache__(data_without_text=data_without_text)
        if self.job.refresh:
            data["refreshed_now"] = True
        else:
            data["refreshed_now"] = False

        # if self.job.debug:
        #     return data, 200
        # else:
        #     return data_without_text, 200

        return data, 200
        # return data_without_text, 200

    def __write_to_cache__(self, data_without_text):
        # We skip writes during testing
        if not self.job.testing:
            write = CheckUrlFileIoV2(
                data=data_without_text,
                hash_based_id=data_without_text["id"],
                file_prefix=self.job.method,
            )
            write.write_to_disk()
