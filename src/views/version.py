from datetime import datetime
from typing import Any, Dict, Optional

from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.views.statistics.write_view import StatisticsWriteView

from src.models.api.job.version_job import VersionJob
from src.models.api.schema.version_schema import VersionSchema

from src.helpers.get_version import get_poetry_version

from src.helpers.cache_utils import get_cache_hash

# import importlib.metadata


class Version(StatisticsWriteView):
    """
    This models all action based on requests from the frontend/patron
    It is instantiated at every request

    This view does not contain any of the checking logic.
    See src/models/checking
    """

    job: Optional[VersionJob] = None
    schema: Schema = VersionSchema()
    # ### serving_from_json: bool = False
    headers: Optional[Dict[str, Any]] = None
    #     {
    #     "Access-Control-Allow-Origin": "*",
    # }
    data: Optional[Dict[str, Any]] = None

    def get(self):
        """This is the main method and the entrypoint for flask
        Every branch in this method has to return a tuple (Any,response_code)"""
        from src import app

        app.logger.debug("Version::get: running")

        self.__validate_and_get_job__()

        # use isInstance in case the job returned is empty, "{}", indicating no request args
        if isinstance(self.job, dict):
            app.logger.debug("Version::get: job validated")
            return self.__return_version__()


    def __return_version__(self):

        version = get_poetry_version("pyproject.toml")
        timestamp = datetime.timestamp(datetime.utcnow())
        isodate = datetime.isoformat(datetime.utcnow())

        data = {
            "version": version,
            "timestamp": int(timestamp),
            "isodate": str(isodate),
            "hash_test": {
                "key": "mister_bungle.com",
                "hash": get_cache_hash("mister_bungle.com"),
            }
        }

        return data, 200
