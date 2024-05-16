# from flask_restful import Resource, abort  # type: ignore
# from marshmallow import Schema
from datetime import datetime
from typing import Any, Optional, Tuple
import traceback

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.v2.file_io.article_file_io_v2 import ArticleFileIoV2
from src.models.v2.job.article_job_v2 import ArticleJobV2
from src.models.v2.schema.article_schema_v2 import ArticleSchemaV2
from src.models.v2.wikimedia.wikipedia.analyzer_v2 import WikipediaAnalyzerV2
from src.models.wikimedia.enums import AnalyzerReturnValues, WikimediaDomain
from src.views.v2.statistics import StatisticsViewV2

from src.helpers.get_version import get_poetry_version


class ArticleV2(StatisticsViewV2):
    """
    returns data associated with article specified by the schema
    """

    schema = ArticleSchemaV2()  # overrides StatisticsViewV2's schema property
    job: ArticleJobV2  # overrides StatisticsViewV2's job property

    page_analyzer: Optional[WikipediaAnalyzerV2] = None

    def __setup_io__(self):
        """
        implementation for StatisticsWriteView.__setup_io__
        """
        self.io = ArticleFileIoV2(job=self.job)

    def __return_article_data__(self):
        from src import app

        app.logger.debug("ArticleV2::__return_article_data__")

        self.__setup_io__()

        if not self.job.refresh:
            self.__read_from_cache__()  # inherited from StatisticsWriteView; fills io.data if successful

        # if self.io.data and not self.job.refresh:
        if self.io.data:
            # cached data has been successfully retrieved - return it
            app.logger.info(
                f"Returning cached articleV2 json data, date: {self.time_of_analysis}"
            )
            return self.io.data, 200

        # no cached data, either cause it doesnt exist or force refresh = true
        app.logger.info("generating articleV2 data (force refresh or no cache)")
        return self.__analyze_and_write_and_return__()

    def get(self):
        """
        main entrypoint for flask
        must return a tuple (Any,response_code)
        """
        from src import app
        app.logger.debug("ArticleV2::get")

        try:
            self.__validate_and_get_job__()
            # inherited from StatisticsWriteView -> StatisticsViewV2
            # sets up job parameters, possibly with some massaging from the @post_load function
            # (@postload is courtesy of the marshmallow module addition)

            # for articles, make sure the lang, title and domain are set
            if (
                self.job.lang == "en"
                and self.job.title
                and self.job.domain == WikimediaDomain.wikipedia
            ) or self.job.url:
                return self.__return_article_data__()

            else:
                return self.__return_article_error__()
        except WikipediaApiFetchError as e:
            return {"error": f"API Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500

    def __return_article_error__(self):
        from src import app

        if self.job.title == "":
            app.logger.error("ArticleV2: ERROR: Title is missing")
            return "Title is missing", 400
        if self.job.domain != "wikipedia":
            app.logger.error("ArticleV2: ERROR: Only 'wikipedia' site is supported")
            return "Only 'wikipedia' site is supported", 400

    def __analyze_and_write_and_return__(self) -> Tuple[Any, int]:
        """
        Analyze, calculate the time, write statistics to disk and return it
        If we did not get statistics, return a meaningful error to the patron
        """

        from src import app

        app.logger.info("ArticleV2::__analyze_and_write_and_return__")

        if not self.page_analyzer:
            self.page_analyzer = WikipediaAnalyzerV2(job=self.job)

        self.io.data = self.page_analyzer.get_article_data()

        # if article not found, return error as such
        if not self.page_analyzer.article_found:
            return AnalyzerReturnValues.NOT_FOUND.value, 404

        # if article is a redirect, return error as such
        if self.page_analyzer.is_redirect:
            app.logger.debug("found redirect")
            return AnalyzerReturnValues.IS_REDIRECT.value, 400

        app.logger.debug("ArticleV2:: processed article, saving...")

        self.__update_time_information__()

        self.__write_to_disk__()
        if not self.io:
            raise MissingInformationError()

        if self.io.data:
            self.io.data["served_from_cache"] = False
            # app.logger.debug("returning dictionary")
            return self.io.data, 200

        else:
            raise MissingInformationError()

    def __update_time_information__(self):
        """Update the dictionary before returning it"""
        if self.io.data:
            timestamp = datetime.timestamp(datetime.utcnow())
            isodate = datetime.isoformat(datetime.utcnow())
            self.io.data["timestamp"] = int(timestamp)
            self.io.data["isodate"] = str(isodate)

        else:
            raise ValueError("self.io.data is not a dict")

    def __write_to_disk__(self):
        """Write both article json and all reference json files"""
        from src import app

        app.logger.debug("ArticleV2:__write_to_disk__")

        if self.job.testing:
            return

        self.__write_article_to_disk__()
        # NB not writung references to disk now...
        # self.__write_references_to_disk__()

    def __write_article_to_disk__(self):
        article_io = ArticleFileIoV2(
            job=self.job,
            data=self.io.data,
            wari_id=self.job.iari_id,  # defined in ArticleJobV2
        )
        article_io.write_to_disk()

    # NB: not writing references at this time
    # def __write_references_to_disk__(self):
    #     references_file_io = ReferencesFileIoV2(
    #         references=self.page_analyzer.reference_statistics
    #     )
    #     references_file_io.write_references_to_disk()
