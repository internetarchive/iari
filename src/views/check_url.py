import hashlib
import logging
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.models.exceptions import MissingInformationError
from src.models.file_io.url_file_io import UrlFileIo

from src.models.api.job.check_url_job import UrlJob
from src.models.api.schema.check_url_schema import UrlSchema
from src.models.identifiers_checking.url import Url

from src.views.statistics.write_view import StatisticsWriteView


logger = logging.getLogger(__name__)


class CheckUrl(StatisticsWriteView):
    """
    This models all action based on requests from the frontend/patron
    It is instantiated at every request

    This view does not contain any of the checking logic.
    See src/models/checking
    """

    job: Optional[UrlJob] = None
    schema: Schema = UrlSchema()
    # ### serving_from_json: bool = False
    headers: Optional[Dict[str, Any]] = None
    #     {
    #     "Access-Control-Allow-Origin": "*",
    # }
    data: Optional[Dict[str, Any]] = None

    @property
    def __url_hash_id__(self) -> str:
        """This generates an 8-char long id based on the md5 hash of
        the raw upper cased URL supplied by the user"""
        if not self.job:
            raise MissingInformationError()

        return hashlib.md5(f"{self.job.unquoted_url.upper()}".encode()).hexdigest()[:8]

    def get(self):
        """This is the main method and the entrypoint for flask
        Every branch in this method has to return a tuple (Any,response_code)"""
        from src import app

        app.logger.debug("get: running")
        self.__validate_and_get_job__()
        if self.job:
            return self.__return_from_cache_or_analyze_and_return__()

    def __setup_io__(self):
        logger.debug(
            f"CheckUrl:__setup_io__: self._url_hash_id = {self.__url_hash_id__}"
        )
        self.io = UrlFileIo(
            hash_based_id=self.__url_hash_id__,
            file_prefix=self.job.method,
        )

    def __return_from_cache_or_analyze_and_return__(self):
        if not self.job.refresh:
            self.__setup_and_read_from_cache__()  # fills self.io.data with cache if found
            if self.io.data:
                return self.io.data, 200
            else:
                return self.__return_fresh_data__()  # self.io.data empty - fetch and cache new value
        else:
            return self.__return_fresh_data__()

    def __return_fresh_data__(self):
        from src import app

        url_string = self.job.unquoted_url
        app.logger.info(f"CheckUrl::__return_fresh_data__: url is {url_string}")
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

        self.__write_to_cache__(data_without_text=data_without_text)
        if self.job.refresh:
            data["refreshed_now"] = True
        else:
            data["refreshed_now"] = False

        if self.job.debug:
            return data, 200
        else:
            return data_without_text, 200

    def __write_to_cache__(self, data_without_text):
        # We skip writes during testing
        if not self.job.testing:
            write = UrlFileIo(
                data=data_without_text,
                hash_based_id=data_without_text["id"],
                file_prefix=self.job.method,
            )
            write.write_to_disk()
