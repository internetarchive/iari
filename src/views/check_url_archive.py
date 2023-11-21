import hashlib
from datetime import datetime
from typing import Any, Dict, Optional

from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.models.api.job.check_url_archive_job import UrlArchiveJob
from src.models.api.schema.check_url_archive_schema import UrlArchiveSchema
from src.models.exceptions import MissingInformationError
from src.models.file_io.url_file_io import UrlFileIo
from src.models.identifiers_checking.url_archive import UrlArchive
from src.views.statistics.write_view import StatisticsWriteView


class CheckUrlArchive(StatisticsWriteView):
    """
    calls iabot's searchurldata method to return archive status
    data, according to iabot's internal database of links
    """

    job: Optional[UrlArchiveJob] = None
    schema: Schema = UrlArchiveSchema()
    serving_from_json: bool = False
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

        self.__validate_and_get_job__()  # StatisticsView::__validate_and_get_job__
        """

        """
        if self.job:
            return self.__return_from_cache_or_analyze_and_return__()

    def __setup_io__(self):
        self.io = UrlFileIo(hash_based_id=self.__url_hash_id__)

    def __return_from_cache_or_analyze_and_return__(self):
        from src import app

        app.logger.debug("__return_from_cache_or_analyze_and_return__; running")

        # always return fresh data for url_archive, for now...
        # in essence, the iabot database really IS the cache...
        return self.__return_fresh_data__()

    def __return_fresh_data__(self):
        from src import app

        url_string = self.job.unquoted_url
        app.logger.info(f"Got {url_string}")

        url_to_archive = UrlArchive(url=url_string)
        url_to_archive.check()

        timestamp = datetime.timestamp(datetime.utcnow())
        isodate = datetime.isoformat(datetime.utcnow())
        url_hash_id = self.__url_hash_id__

        data = url_to_archive.get_dict
        data["timestamp"] = int(timestamp)
        data["isodate"] = str(isodate)
        data["id"] = url_hash_id

        return data, 200
