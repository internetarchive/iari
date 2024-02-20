from datetime import datetime
from typing import Optional

from flask import request
from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.helpers.console import console

# from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer
from src.models.api.job import Job
from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo


class StatisticsViewV2(Resource):
    """Abstract class for endpoints writing to disk

    current classes that inherit this:
    - ArticleV2

    the StatisticsWriteView inherits this class.
    """

    schema: Optional[Schema] = None
    job: Optional[Job]
    # derived class sets this

    time_of_analysis: Optional[datetime] = None
    serving_from_json: bool = False

    io: Optional[FileIo] = None

    # wikipedia_page_analyzer: Optional[WikipediaAnalyzer] = None
    # # TODO this should not be defined in this class - it should live in wiki article class
    # # FIXME get rid of this here (must fix/change in view/statistics/article.py)

    # these are placed here experimentaly...seeif it works!

    # derived ("child") class must implement __setup_io__ from this base ("parent") class
    def __setup_io__(self):
        raise NotImplementedError()

    def __setup_and_read_from_cache__(self):
        self.__setup_io__()  # sets up "io" property as FileIo instance
        self.io.read_from_disk()

    def __read_from_cache__(self):
        if self.io:
            self.io.read_from_disk()

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

        app.logger.debug("before self.schema.load")
        self.job = self.schema.load(request.args)
        app.logger.debug("after self.schema.load")
        if not self.job:
            console.print("self.job is null")

        console.print(self.job)
