import hashlib
from datetime import datetime
from typing import Any, Dict, Optional

from src.models.api.check_doi.check_doi_schema import CheckDoiSchema
from src.models.api.job.check_doi_job import CheckDoiJob
from src.models.exceptions import MissingInformationError
from src.models.file_io.doi_file_io import DoiFileIo
from src.models.identifiers_checking.doi import Doi
from src.views.statistics import StatisticsView


class CheckDoi(StatisticsView):
    """
    This models all action based on requests from the frontend/patron
    It is instantiated at every request

    This view does not contain any of the checking logic.
    See src/models/checking
    """

    job: Optional[CheckDoiJob] = None
    schema: CheckDoiSchema = CheckDoiSchema()
    serving_from_json: bool = False
    headers: Dict[str, Any] = {
        "Access-Control-Allow-Origin": "*",
    }
    data: Dict[str, Any] = {}

    def get(self):
        """This is the main method and the entrypoint for flask
        Every branch in this method has to return a tuple (Any,response_code)"""
        from src.models.api import app

        app.logger.debug("get: running")
        self.__validate_and_get_job__()
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
        return data, 200

    @property
    def __doi_hash_id__(self) -> str:
        """This generates an 8-char long id based on the md5 hash of
        the raw upper cased doi supplied by the user"""
        if not self.job:
            raise MissingInformationError()
        return hashlib.md5(f"{self.job.doi.upper()}".encode()).hexdigest()[:8]
