import hashlib
from datetime import datetime
from typing import Any, Dict, Optional

from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.models.api.check_url.check_url_schema import CheckUrlSchema
from src.models.api.job.check_url_job import CheckUrlJob
from src.models.exceptions import MissingInformationError
from src.models.file_io.url_file_io import UrlFileIo
from src.models.identifiers_checking.url import Url
from src.views.statistics import StatisticsView
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    easter_island_short_tail_excerpt,
    easter_island_tail_excerpt,
    electrical_breakdown_full_article,
    test_full_article,
)


class CheckUrl(StatisticsView):
    """
    This models all action based on requests from the frontend/patron
    It is instantiated at every request

    This view does not contain any of the checking logic.
    See src/models/checking
    """

    job: Optional[CheckUrlJob] = None
    schema: Schema = CheckUrlSchema()
    serving_from_json: bool = False
    headers: Dict[str, Any] = {
        "Access-Control-Allow-Origin": "*",
    }
    data: Dict[str, Any] = {}

    @property
    def __url_hash_id__(self) -> str:
        """This generates an 8-char long id based on the md5 hash of
        the raw upper cased URL supplied by the user"""
        if not self.job:
            raise MissingInformationError()
        return hashlib.md5(f"{self.job.url.upper()}".encode()).hexdigest()[:8]

    def get(self):
        """This is the main method and the entrypoint for flask
        Every branch in this method has to return a tuple (Any,response_code)"""
        from src.models.api import app

        app.logger.debug("get: running")
        self.__validate_and_get_job__()
        # we default to 2 second timeout
        url = Url(url=self.job.url, timeout=self.job.timeout)
        url.check()
        data = url.get_dict()
        timestamp = datetime.timestamp(datetime.utcnow())
        data["timestamp"] = int(timestamp)
        isodate = datetime.isoformat(datetime.utcnow())
        data["isodate"] = str(isodate)
        url_hash_id = self.__url_hash_id__
        data["id"] = url_hash_id
        write = UrlFileIo(data=data, hash_based_id=url_hash_id)
        write.write_to_disk()
        return data, 200
