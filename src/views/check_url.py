import hashlib
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional, ClassVar

from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.models.api.job.check_url_job import UrlJob
from src.models.api.schema.check_url_schema import UrlSchema
from src.models.exceptions import MissingInformationError
from src.models.file_io.url_file_io import UrlFileIo
from src.models.identifiers_checking.url import Url
from src.views.statistics.write_view import StatisticsWriteView


class CheckUrl(StatisticsWriteView):
    """
    This models all action based on requests from the frontend/patron
    It is instantiated at every request

    This view does not contain any of the checking logic.
    See src/models/checking
    """

    job: Optional[UrlJob] = None
    schema: Schema = UrlSchema()
    serving_from_json: bool = False
    headers: ClassVar[Dict[str, Any]] = {
        "Access-Control-Allow-Origin": "*",
    }
    data: ClassVar[Dict[str, Any]] = {}

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
        self.io = UrlFileIo(hash_based_id=self.__url_hash_id__)

    def __return_from_cache_or_analyze_and_return__(self):
        from src import app

        app.logger.debug("__handle_valid_job__; running")

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
        app.logger.info(f"Got {url_string}")
        url = Url(url=url_string, timeout=self.job.timeout)
        url.check()
        data = url.get_dict
        timestamp = datetime.timestamp(datetime.utcnow())
        data["timestamp"] = int(timestamp)
        isodate = datetime.isoformat(datetime.utcnow())
        data["isodate"] = str(isodate)
        url_hash_id = self.__url_hash_id__
        data["id"] = url_hash_id
        data_without_text = deepcopy(data)
        del data_without_text["text"]
        self.__write_to_cache__(data_without_text=data_without_text)
        if self.job.refresh:
            self.__print_log_message_about_refresh__()
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
                data=data_without_text, hash_based_id=data_without_text["id"]
            )
            write.write_to_disk()
