# from flask_restful import Resource, abort  # type: ignore
# from marshmallow import Schema
from datetime import datetime
from typing import Any, Optional, Tuple
import traceback

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError

from src.models.v2.file_io.article_cache_file_io_v2 import ArticleCacheFileIoV2
from src.models.v2.job.article_cache_job_v2 import ArticleCacheJobV2
from src.models.v2.schema.article_cache_schema_v2 import ArticleCacheSchemaV2

from src.models.v2.wikimedia.wikipedia.analyzer_v2 import WikipediaAnalyzerV2
from src.models.wikimedia.enums import AnalyzerReturnValues, WikimediaDomain
from src.views.v2.statistics import StatisticsViewV2

from src.helpers.get_version import get_poetry_version


class ArticleCacheV2(StatisticsViewV2):
    """
    returns data associated with parsed article data specified by iari_id.
    assumes article data has been cached and is referenced bu iari_id
    """

    schema = ArticleCacheSchemaV2()  # overrides StatisticsViewV2's schema property
    job: ArticleCacheJobV2  # overrides StatisticsViewV2's job property

    def __setup_io__(self):
        """
        implementation for StatisticsWriteView.__setup_io__
        """
        self.io = ArticleCacheFileIoV2(job=self.job)

    def __return_article_data__(self):
        from src import app

        app.logger.debug("ArticleCacheV2::__return_article_data__")

        self.__setup_io__()  # defined right above!

        self.__read_from_cache__()  # inherited from StatisticsWriteView; fills io.data if successful

        # if self.io.data and not self.job.refresh:
        if self.io.data:
            # cached data has been successfully retrieved - return it
            app.logger.info(
                f"Returning cached articleV2 json data, date: {self.time_of_analysis}"
            )
            return self.io.data, 200

        # else no cache, so return"no cached data" error


    def get(self):
        """
        main entrypoint for flask
        must return a tuple (Any,response_code)
        """
        from src import app
        app.logger.debug("ArticleCacheV2::get")

        try:
            self.__validate_and_get_job__()
            # inherited from StatisticsWriteView -> StatisticsViewV2
            # sets up job parameters, possibly with some massaging from the @post_load function
            # (@postload is courtesy of the marshmallow module addition)

            if self.job.iari_id:
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

        if self.job.iari_id == "":
            app.logger.error("ArticleCacheV2: ERROR: iari_id is missing")
            return "iari_id is missing", 400
