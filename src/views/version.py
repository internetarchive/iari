from datetime import datetime
from typing import Any, Dict, Optional

from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.models.api.job.version_job import VersionJob
from src.models.api.schema.version_schema import VersionSchema
from src.views.statistics.write_view import StatisticsWriteView

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
    serving_from_json: bool = False
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
        data = {}

        # trying to get version from metadata but not successful
        # https://stackoverflow.com/questions/11705055/get-full-package-module-name
        # s = inspect.stack()
        # module_name = inspect.getmodule(s[1][0]).__name__
        # my_version = importlib.metadata.version("src")
        my_version = "4.1.3"  # for now
        data["version"] = my_version

        timestamp = datetime.timestamp(datetime.utcnow())
        data["timestamp"] = int(timestamp)
        isodate = datetime.isoformat(datetime.utcnow())
        data["isodate"] = str(isodate)

        return data, 200
