from datetime import datetime
from typing import Any, Tuple

from flask_restful import Resource, abort  # type: ignore

from src.models.api.job.article_job import ArticleJob
from src.models.api.schema.article_schema import ArticleSchema
from src.models.exceptions import MissingInformationError
from src.models.file_io.article_file_io import ArticleFileIo
from src.models.file_io.references import ReferencesFileIo
from src.models.wikimedia.enums import AnalyzerReturn, WikimediaDomain
from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer
from src.views.statistics.write_view import StatisticsWriteView


class Article(StatisticsWriteView):
    """This models the get-statistics API
    It is instantiated at every request"""

    schema = ArticleSchema()
    job: ArticleJob

    def __analyze_and_write_and_return__(self) -> Tuple[Any, int]:
        """Analyze, calculate the time, write statistics to disk and return it
        If we did not get statistics, return a meaningful error to the patron"""
        from src import app

        app.logger.info("__analyze_and_write_and_return__: running")
        if not self.wikipedia_analyzer:
            raise MissingInformationError("self.wikipedia_analyzer was None")
        self.__get_statistics__()
        if self.wikipedia_analyzer.found:
            app.logger.debug("found article")
            if self.wikipedia_analyzer.is_redirect:
                app.logger.debug("found redirect")
                return AnalyzerReturn.IS_REDIRECT.value, 400
            else:
                app.logger.debug("adding time information and returning the statistics")
                self.__update_statistics_with_time_information__()
                # app.logger.debug(f"dictionary from analyzer: {self.statistics_dictionary}")
                # we got a json response
                # according to https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view
                # flask calls jsonify automatically
                self.__write_to_disk__()
                if not self.io:
                    raise MissingInformationError()
                self.io.data["served_from_cache"] = False
                # app.logger.debug("returning dictionary")
                return self.io.data, 200
        else:
            return AnalyzerReturn.NOT_FOUND.value, 404

    def __handle_valid_job__(self):
        from src import app

        app.logger.debug("got valid job")
        self.__read_from_cache__()
        if self.io.data and not self.job.refresh:
            app.logger.info("trying to read from cache")
            self.__read_from_cache__()
            if self.io.data:
                # We got the statistics from json, return them as is
                app.logger.info(
                    f"Returning existing json from disk with date: {self.time_of_analysis}"
                )
                return self.io.data, 200
        else:
            app.logger.info("got refresh from patron")
            # This will run if we did not return an analysis from disk yet
            self.__print_log_message_about_refresh__()
            self.__setup_wikipedia_analyzer__()
            return self.__analyze_and_write_and_return__()

    def __get_statistics__(self):
        from src import app

        app.logger.debug("__get_statistics__: running")
        if not self.wikipedia_analyzer:
            raise MissingInformationError("self.wikipedia_analyzer was None")
        # https://realpython.com/python-timer/
        self.__setup_io__()
        self.io.data = self.wikipedia_analyzer.get_statistics()

    def __update_statistics_with_time_information__(self):
        """Update the dictionary before returning it"""
        if self.io.data:
            timestamp = datetime.timestamp(datetime.utcnow())
            self.io.data["timestamp"] = int(timestamp)
            isodate = datetime.isoformat(datetime.utcnow())
            self.io.data["isodate"] = str(isodate)
        else:
            raise ValueError("not a dict")

    def __write_to_disk__(self):
        """Write both article json and all reference json files"""
        from src import app

        app.logger.debug("__write_to_disk__: running")
        if not self.job.testing:
            self.__write_article_to_disk__()
            self.__write_references_to_disk__()

    def __return_meaningful_error__(self):
        from src import app

        app.logger.error("__return_meaningful_error__: running")
        if self.job.title == "":
            return "Title was missing", 400
        if self.job.domain != "wikipedia":
            return "Only 'wikipedia' site is supported", 400

    def __setup_wikipedia_analyzer__(self):
        if not self.wikipedia_analyzer:
            from src import app

            app.logger.info(f"Analyzing {self.job.title}...")
            self.wikipedia_analyzer = WikipediaAnalyzer(job=self.job, check_urls=True)

    def get(self):
        """This is the main method and the entrypoint for flask
        Every branch in this method has to return a tuple (Any,response_code)"""
        from src import app

        app.logger.debug("get: running")
        self.__validate_and_get_job__()
        if (
            self.job.lang == "en"
            and self.job.title
            and self.job.domain == WikimediaDomain.wikipedia
        ) or self.job.url:
            return self.__handle_valid_job__()
        else:
            return self.__return_meaningful_error__()

    def __setup_io__(self):
        self.io = ArticleFileIo(job=self.job)

    def __write_article_to_disk__(self):
        article_io = ArticleFileIo(
            job=self.job,
            data=self.io.data,
            wari_id=self.job.wari_id,
        )
        article_io.write_to_disk()

    def __write_references_to_disk__(self):
        references_file_io = ReferencesFileIo(
            references=self.wikipedia_analyzer.reference_statistics
        )
        references_file_io.write_references_to_disk()
