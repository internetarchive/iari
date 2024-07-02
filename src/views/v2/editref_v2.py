# from flask_restful import Resource, abort  # type: ignore
# from marshmallow import Schema
from datetime import datetime
from typing import Any, Optional, Tuple
import traceback

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError

from src.models.v2.schema.editref_schema_v2 import EditRefSchemaV2
from src.models.v2.job.editref_job_v2 import EditRefJobV2

# from src.models.v2.file_io.article_file_io_v2 import ArticleFileIoV2
# from src.models.v2.wikimedia.wikipedia.analyzer_v2 import WikipediaAnalyzerV2
# from src.models.wikimedia.enums import AnalyzerReturnValues, WikimediaDomain
from src.views.v2.statistics import StatisticsViewV2


from src.helpers.get_version import get_poetry_version


class EditRefV2(StatisticsViewV2):
    # TODO Since no setup_io is needed for this endpoint, we could maybe
    #   base this on an "Execution" view? or a generic "Action" view?

    """
    replaces search string with replace string in source string, and returns results
    """

    schema = EditRefSchemaV2()  # overrides StatisticsViewV2's schema property
    job: EditRefJobV2           # overrides StatisticsViewV2's job property

    replaced_data = ""

    def get(self):
        """
        flask GET entrypoint for returning editref results
        must return a tuple: (Any,response_code)
        """
        from src import app
        app.logger.debug("==> EditRefV2::get")

        return self.__process_data__()

    def post(self):
        """
        flask POST entrypoint for returning editref results
        must return a tuple: (Any,response_code)
        """
        from src import app
        app.logger.debug("==> EditRefV2::post")

        return self.__process_data__(method="post")


    def __process_data__(self, method="get"):
        from src import app
        try:
            self.__validate_and_get_job__(method)  # inherited from StatisticsViewV2
            #
            # validates via schema (a marshmallow feature) and sets job values wia schema's values

            # set up results
            self.__replace_data__()  # sets self.replaced_data

            # and return results
            return {
                "target": self.job.target,
                "replace": self.job.replace,
                "source": self.job.source,
                "result": self.replaced_data
            }

        except MissingInformationError as e:
            app.logger.debug("after EditRefV2::self.__validate_and_get_job__ MissingInformationError exception")
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            app.logger.debug("after EditRefV2::self.__validate_and_get_job__ exception")
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500

    def __replace_data__(self):
        from src import app
        app.logger.debug("==> EditRefV2::__replace_data__")

        self.replaced_data = self.job.source.replace(self.job.target, self.job.replace)


