import hashlib
from datetime import datetime
from typing import Any, Dict, Optional

from src.models.api.handlers.xhtml import XhtmlHandler
from src.models.api.job.check_url_job import UrlJob
from src.models.api.schema.check_url_schema import UrlSchema
from src.models.exceptions import MissingInformationError
from src.models.file_io.xhtml_file_io import XhtmlFileIo
from src.views.statistics.write_view import StatisticsWriteView


class Xhtml(StatisticsWriteView):
    """
    This models all action based on requests from the frontend/patron
    It is instantiated at every request
    """

    job: Optional[UrlJob] = None
    schema: UrlSchema = UrlSchema()
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
        self.io = XhtmlFileIo(hash_based_id=self.__url_hash_id__)

    def __return_from_cache_or_analyze_and_return__(self):
        from src import app

        app.logger.debug("__handle_valid_job__; running")

        self.__setup_and_read_from_cache__()
        if self.io.data and not self.job.refresh:
            return self.io.data, 200
        else:
            url_string = self.job.unquoted_url
            app.logger.info(f"Got {url_string}")
            handler = XhtmlHandler(job=self.job)
            handler.download_and_extract()
            if handler.error:
                return handler.error_details, 400
            data = handler.get_dict()
            # console.print(data)
            # exit()
            timestamp = datetime.timestamp(datetime.utcnow())
            data["timestamp"] = int(timestamp)
            isodate = datetime.isoformat(datetime.utcnow())
            data["isodate"] = str(isodate)
            url_hash_id = self.__url_hash_id__
            data["id"] = url_hash_id
            # We don't write during tests because it breaks the CI
            if not self.job.testing:
                write = XhtmlFileIo(data=data, hash_based_id=url_hash_id)
                write.write_to_disk()
            if self.job.refresh:
                self.__print_log_message_about_refresh__()
                data["refreshed_now"] = True
            else:
                data["refreshed_now"] = False
            return data, 200
