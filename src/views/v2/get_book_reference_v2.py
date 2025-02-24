# from flask_restful import Resource, abort  # type: ignore
# from marshmallow import Schema
from datetime import datetime
from typing import Any, Optional, Tuple
import traceback

from dateutil.parser import isoparse

import config
import requests

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError

from src.models.v2.job.get_book_reference_job import GetBookReferenceJobV2
from src.models.v2.schema.get_book_reference_schema_v2 import GetBookReferenceSchemaV2

# from src.models.v2.file_io.article_file_io_v2 import ArticleFileIoV2
# from src.models.v2.wikimedia.wikipedia.analyzer_v2 import WikipediaAnalyzerV2
# from src.models.wikimedia.enums import AnalyzerReturnValues, WikimediaDomain
from src.views.v2.statistics import StatisticsViewV2


from src.helpers.get_version import get_poetry_version


class GetBookReferenceV2(StatisticsViewV2):

    """
    returns version of media that shows the book being referenced
    Soon, this shall return a snippet from archive.org's book snippet idea
    While that's being implemented, the response output is just hard-coded
    """

    schema = GetBookReferenceSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: GetBookReferenceJobV2           # Holds usable variables, seeded from schema. Overrides StatisticsViewV2's "job"

    book_data = {}

    def get(self):
        """
        flask GET entrypoint for returning get_book_reference results
        must return a tuple: (Any,response_code)
        """
        from src import app
        app.logger.debug("==> GetBookReferenceV2::get")

        return self.__process_data__(method="get")

    def post(self):
        """
        flask POST entrypoint for returning editref results
        """
        from src import app
        app.logger.debug("==> GetBookReferenceV2::post")

        return self.__process_data__(method="post")


    def __process_data__(self, method="get"):
        """
        must return a tuple: (Any,response_code)
        """
        from src import app
        try:
            self.__validate_and_get_job__(method)  # inherited from StatisticsViewV2
            #
            # validates schema params (a marshmallow feature), and sets job properties based on schema's values

            self.__get_book_data__()  # fills self.book_data

            # and return book_data, which should be like:
            # {
            #     "title" : "A Book",
            #     "pages" : "238"
            #     "image": "ABCDEFGBASE64GOBLYGOOKGOESHERE",
            # }
            return self.book_data


        except MissingInformationError as e:
            app.logger.debug("after GetBookReferenceV2::self.__validate_and_get_job__ MissingInformationError exception")
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            app.logger.debug("after GetBookReferenceV2::self.__validate_and_get_job__ exception")
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500

    def __get_book_data__(self):
        # takes source_text and applies replacement transformations on it
        from src import app
        app.logger.debug("==> GetBookReferenceV2::__get_book_data__")

        # this is where we reach out to internet archive and get book citation snippet

        self.book_data = {
            "title": "A Book",
            "pages": "238",
            "image": "ABCDEFGBASE64GOBLYGOOKGOESHERE",
        }



