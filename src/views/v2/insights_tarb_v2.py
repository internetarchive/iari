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

from src.models.v2.job.insights_tarb_job_v2 import InsightsTarbJobV2
from src.models.v2.schema.insights_tarb_schema_v2 import InsightsTarbSchemaV2


class InsightsTarbV2(StatisticsViewV2):

    """
    returns IABot statistical data
    """

    schema = InsightsTarbSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: InsightsTarbJobV2           # Holds usable variables, seeded from schema. Overrides StatisticsViewV2's "job"

    return_data: Dict[str, Any] = {}  # holds parsed data from data processing
    execution_errors: List[Dict[str, Any]] = None

    def get(self):
        """
        flask entrypoint for GET
        must return a tuple: (Any, response_code)
        """
        from src import app
        app.logger.debug(f"==> InsightsTarbV2::get")

        return self.__process_request__(method=RequestMethods.get)


    def __process_request__(self, method=RequestMethods.post):  # default to POST method

        from src import app
        app.logger.debug(f"==> InsightsTarbV2::__process_request__, method = {method}")

        # Start the timer
        start_time = time.time()

        # fetch the insight data
        try:

            # validate and setup params
            self.__validate_and_get_job__(method)  # inherited/subclassed from StatisticsViewV2

            # fetch the data, parse and return summary
            insight_data = self.__get_insight_data__()

            # Stop the timer and calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time

            self.return_data = {
                "iari_version": get_poetry_version("pyproject.toml"),
                "iari_command": "tarb_insights",
                "endpoint": request.endpoint,
                "execution_time": f"{execution_time:.4f} seconds",
                "execution_errors": self.execution_errors,
            }

            self.return_data.update(insight_data)

            return self.return_data, 200


        except MissingInformationError as e:
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500


    def __get_insight_data__(self):
        """
        grabs appropriate data regarding media updates
        """

        # soup = self.__get_stats_soup__()
        #
        # table_names = self.__get_table_names__(soup)
        # table_list = self.__get_all_tables__(soup, table_names)
        # table_totals = self.__get_table_totals__(table_list)
        #
        # return {
        #     "table_names": table_names,
        #     "table_totals": table_totals,
        #     "tables": table_list
        # }


        """
        format of each returned record:
        
        {
            "Wiki": "afwiki",
            "Timestamp": "2021-08-14 00:00:00",
            "TotalEdits": 2709,
            "TotalLinks": 3543,
            "ReactiveEdits": 1620,
            "ProactiveEdits": 90,
            "DeadEdits": 278,
            "UnknownEdits": 721,
            "LiveLinks": 163,
            "DeadLinks": 2640,
            "TagLinks": 740,
            "UnknownLinks": 0
        },
        """

        tarb_api_url = "https://iabot.wmcloud.org/api.php?action=statistics&format=flat"

        r = requests.get(url_stats_yearly)
        # TODO use a try/catch here

        if r.status_code != 200:
            return None

        return {
            "test_value_1": 1,
            "test_value_2": 2,
            "test_value_3": 3,
        }


