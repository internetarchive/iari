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

    the StatisticsWriteView inherits this class.
    """

    schema: Optional[Schema] = None
    job: Optional[Job]

    time_of_analysis: Optional[datetime] = None
    # ### serving_from_json: bool = False

    io: Optional[FileIo] = None

    wikipedia_page_analyzer: Optional[WikipediaAnalyzer] = None
    # TODO this should not be defined in this class - it should live in wiki article class
    # FIXME get rid of this here (must fix/change in view/statistics/article.py)

    def __validate_and_get_job__(self):
        """Helper method"""
        self.__validate__()
        self.__parse_into_job__()

    def __validate__(self):
        from src import app

        app.logger.debug("StatisticsView::__validate__")

        errors = self.schema.validate(request.args)
        if errors:
            app.logger.debug(f"Found errors: {errors}")
            abort(400, error=str(errors))
            # TODO check the content of errors here to maybe give a better error return to client

    def __parse_into_job__(self):
        from src import app

        app.logger.debug("__parse_into_job__: running")
        # app.logger.debug(request.args)
        if not self.schema:
            raise MissingInformationError()

        self.job = self.schema.load(request.args)
        if not self.job:
            # this seems to be the case when there are no arguments, as in the
            # /version endpoint. Seems to be harmless not having a valid job property
            console.print("self.job is null")

        console.print(self.job)
