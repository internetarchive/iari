from typing import Any, Optional, Tuple, List, Dict
import traceback
import time

import requests
from bs4 import BeautifulSoup, NavigableString
from flask import request

from src.helpers.get_version import get_poetry_version

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.wikimedia.enums import RequestMethods
from src.views.v2.statistics import StatisticsViewV2
from src.helpers.wiki_utils import WikiUtils

from src.models.v2.job.insights_wiki_job_v2 import InsightsWikiJobV2
from src.models.v2.schema.insights_wiki_schema_v2 import InsightsWikiSchemaV2


class InsightsWikiV2(StatisticsViewV2):
    """
    returns IABot statistical data
    """

    schema = InsightsWikiSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: InsightsWikiJobV2           # Holds usable variables, seeded from schema. Overrides StatisticsViewV2's "job"

    return_data: Dict[str, Any] = {}  # holds parsed data from page processing
    execution_errors: List[Dict[str, Any]] = None

    def get(self):
        """
        flask entrypoint for GET
        must return a tuple: (Any, response_code)
        """
        from src import app
        app.logger.debug(f"==> InsightsWikiV2::get")

        return self.__process_request__(method=RequestMethods.get)


    def __process_request__(self, method=RequestMethods.post):  # default to POST method

        from src import app
        app.logger.debug(f"==> InsightsWikiV2::__process_request__, method = {method}")

        # Start the timer
        start_time = time.time()

        # fetch the insight data
        try:

            # validate and setup params
            self.__validate_and_get_job__(method)  # inherited/subclassed from StatisticsViewV2

            # fetch the data, parse and return summary
            exturl_data = WikiUtils.get_exturls()

            # Stop the timer and calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time
            #         timestamp = datetime.timestamp(datetime.utcnow())
            #         isodate = datetime.isoformat(datetime.utcnow())

            self.return_data = {
                "iari_version": get_poetry_version("pyproject.toml"),
                "iari_command": "wiki_insights",
                "endpoint": request.endpoint,
                "execution_time": f"{execution_time:.4f} seconds",
                "execution_errors": self.execution_errors,
            }

            self.return_data.update(exturl_data)

            return self.return_data, 200


        except MissingInformationError as e:
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500


