from datetime import datetime
from typing import Optional

from flask import request
from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.helpers.console import console
from src.models.api.job import Job
from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo
from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer


class StatisticsView(Resource):
    """Abstract class modeling a statistic endpoint

    We currently have 3 implementations:
    article, references and reference

    They all need to know the wikimedia site, language and title
    so we have this abstract class to verify we got what we need.
    """

    schema: Optional[Schema] = None
    job: Optional[Job]
    wikipedia_analyzer: Optional[WikipediaAnalyzer] = None
    time_of_analysis: Optional[datetime] = None
    serving_from_json: bool = False
    io: Optional[FileIo] = None

    def __validate_and_get_job__(self):
        """Helper method"""
        self.__validate__()
        self.__parse_into_job__()

    def __validate__(self):
        from src import app

        app.logger.debug("__validate__: running")

        errors = self.schema.validate(request.args)
        if errors:
            app.logger.debug(f"Found errors: {errors}")
            abort(400, error=str(errors))

    def __parse_into_job__(self):
        from src import app

        app.logger.debug("__parse_into_job__: running")
        # app.logger.debug(request.args)
        if not self.schema:
            raise MissingInformationError()

        self.job = self.schema.load(request.args)
        if not self.job:
            console.print("self.job is null")

        console.print(self.job)

    def __print_log_message_about_refresh__(self):
        from src import app

        if self.job.refresh:
            app.logger.info("got force refresh from patron")

    # def __write_to_disk__(self):
    #     raise NotImplementedError()
