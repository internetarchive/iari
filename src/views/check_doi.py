import hashlib
from datetime import datetime
from typing import Any, Dict, Optional

from src.models.api.job.check_doi_job import CheckDoiJob
from src.models.api.schema.check_doi_schema import CheckDoiSchema
from src.models.exceptions import MissingInformationError
from src.models.file_io.doi_file_io import DoiFileIo
from src.models.identifiers_checking.doi import Doi
from src.views.statistics.write_view import StatisticsWriteView


class CheckDoi(StatisticsWriteView):
    """
    This models all action based on requests from the frontend/patron
    It is instantiated at every request

    This view does not contain any of the checking logic.
    See src/models/checking
    """

    job: Optional[CheckDoiJob] = None
    schema: CheckDoiSchema = CheckDoiSchema()
    serving_from_json: bool = False
    headers: Optional[Dict[str, Any]] = None
    # {
    #         "Access-Control-Allow-Origin": "*",
    #     }
    data: Optional[Dict[str, Any]] = None

    def get(self):
        """This is the main method and the entrypoint for flask
        Every branch in this method has to return a tuple (Any,response_code)"""
        from src import app

        app.logger.debug("get: running")
        self.__validate_and_get_job__()
        if self.job:
            return self.__return_from_cache_or_analyze_and_return__()

    def __return_from_cache_or_analyze_and_return__(self):
        from src import app

        app.logger.debug("__handle_valid_job__; running")

        self.__setup_and_read_from_cache__()
        if self.io.data and not self.job.refresh:
            return self.io.data, 200
        else:
            doi_string = self.job.unquoted_doi
            app.logger.info(f"Got {doi_string}")
            doi = Doi(doi=doi_string, timeout=self.job.timeout)
            doi.lookup_doi()
            data = doi.get_doi_dictionary()
            timestamp = datetime.timestamp(datetime.utcnow())
            data["timestamp"] = int(timestamp)
            isodate = datetime.isoformat(datetime.utcnow())
            data["isodate"] = str(isodate)
            doi_hash_id = self.__doi_hash_id__
            data["id"] = doi_hash_id
            write = DoiFileIo(data=data, hash_based_id=doi_hash_id)
            write.write_to_disk()
            if self.job.refresh:
                self.__print_log_message_about_refresh__()
                data["refreshed_now"] = True
            else:
                data["refreshed_now"] = False
            return data, 200

    def __setup_io__(self):
        self.io = DoiFileIo(hash_based_id=self.__doi_hash_id__)

    @property
    def __doi_hash_id__(self) -> str:
        """This generates an 8-char long id based on the md5 hash of
        the raw upper cased doi supplied by the user"""
        if not self.job:
            raise MissingInformationError()
        return hashlib.md5(f"{self.job.doi.upper()}".encode()).hexdigest()[:8]
