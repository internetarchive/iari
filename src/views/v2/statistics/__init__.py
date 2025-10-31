from datetime import datetime
from typing import Optional, Any

from flask import request
from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.helpers.console import console

from src.models.api.job import Job
from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo
from src.models.wikimedia.enums import RequestMethods


class StatisticsViewV2(Resource):
    """
    Abstract class for endpoints writing to disk and/or processing request args

    classes that inherit this:
    - ArticleV2
    - ArticleCacheV2
    - EditRefV2

    """

    # derived class sets these
    schema: Optional[Schema] = None  # uses schema.validate to validate
    job: Optional[Job]  # loads parameters via schema.load
    io: Optional[FileIo] = None  # derived class must implement __setup_io__

    request_args: Any = {}
    time_of_analysis: Optional[datetime] = None

    def __setup_io__(self):
        # Derived child class must implement __setup_io__ from this base parent class
        raise NotImplementedError()  # must be defined in parent class

    def __setup_and_read_from_cache__(self):
        self.__setup_io__()  # sets up "io" property as FileIo instance
        self.io.read_from_disk()

    def __read_from_cache__(self):
        if self.io:
            self.io.read_from_disk()

    def __validate_and_get_job__(self, method=RequestMethods.get):
        """
        Validates request params, whether from GET or POST, and,
        if successful, pulls param values into job's properties
        """

        # get request args via GET or POST
        self.request_args = request.args if (request.method == "GET") else request.form

        from src import app
        app.logger.debug(f"==> StatisticsViewV2::__validate_and_get_job__: request.method = {request.method}; request_args: {self.request_args}")

        self.__validate__()
        self.__parse_into_job__()

    def __validate__(self):

        from src import app
        app.logger.debug(f"==> StatisticsViewV2::__validate__({self.request_args})")

        errors = self.schema.validate(self.request_args)
        if errors:
            app.logger.debug(f"StatisticsViewV2 Validation errors: {errors}")
            raise MissingInformationError(errors)


    def __parse_into_job__(self):

        from src import app
        app.logger.debug(f"==> StatisticsViewV2::__parse_into_job__({self.request_args})")

        if not self.schema:
            raise MissingInformationError("No schema set for StatisticsViewV2")

        # populate job object with mapped values from request_args
        self.job = self.schema.load(self.request_args)

        if not self.job:
            # This seems to be the case when there are no arguments, as in the
            # /version endpoint. Seems to be harmless not having a valid job property
            app.logger.info("StatisticsViewV2: self.job is null")

        console.print("=== JOB ===")
        console.print(self.job)
