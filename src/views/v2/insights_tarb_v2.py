from typing import Any, Optional, Tuple, List, Dict
import traceback
import time
import datetime
# import pandas as pd

import requests
from bs4 import BeautifulSoup, NavigableString
from flask import request

from src.helpers.get_version import get_poetry_version

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError, TarbFetchError
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

    STATSAPI = "https://iabot.wmcloud.org/api.php?action=statistics&format=flat&only-year={}"
    # STRYEAR = 2016
    STRYEAR = 2023
    ENDYEAR = datetime.date.today().year

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

            # seed the return data with the job params
            self.return_data = {
                "iari_version": get_poetry_version("pyproject.toml"),
                "iari_command": "tarb_insights",
                "endpoint": request.endpoint,
                "execution_time": f"{execution_time:.4f} seconds",
                "execution_errors": self.execution_errors,
            }

            # and append the insight data we really want!
            self.return_data.update(insight_data)

            return self.return_data, 200


        except MissingInformationError as e:
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except TarbFetchError as e:
            traceback.print_exc()
            return {"error": f"Error fetching TARB info: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500


    def __get_insight_data__(self):
        try:
            raw_data = self.__get_raw_insight_data__()
        except Exception as e:
            raise TarbFetchError(f"Problem getting raw TARB stats ({str(e)})")

        try:
            summary_data = self.__get_summary_insight_data__(raw_data)
        except Exception as e:
            raise TarbFetchError(f"Problem summarizing TARB stats ({str(e)})")


        return {
            "raw_data": raw_data,
            "summary_data": summary_data,
        }
    
    
    def __get_raw_insight_data__(self):
        """
        grabs edit data from IABot
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

        return self.__get_raw_data__()

        #
        # def load_yearly_data(year):
        #     df = pd.DataFrame(requests.get(STATSAPI.format(year)).json()["statistics"])
        #     # TODO may want to decorate api url with filtering to reduce file size over the wire
        #
        #     df["DateTime"] = df["Timestamp"].str[:10] + "T12:00:00Z"
        #     df["YearMonth"] = df["Timestamp"].str[:8] + "15"
        #     df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        #     return df
        #
        # # tarb_api_url = "https://iabot.wmcloud.org/api.php?action=statistics&format=flat"
        # # tarb_api_url = "https://iabot.wmcloud.org/api.php?action=statistics&format=flat"
        # # https: // iabot.wmcloud.org / api.php?action = statistics & format = flat & only - year = 2025 & only - key = DeadEdits
        # def load_data():
        #     return pd.concat([load_yearly_data(y) for y in range(STRYEAR, ENDYEAR)] + [load_yearly_data(ENDYEAR)])
        #
        # try:
        #     df_all_data = load_data()
        #
        # except Exception as e:
        #     raise TarbFetchError(f"X2 Problem fetching raw TARB stats: ({str(e)})")
        #
        # return df_all_data.to_dict("records")
        #

    def __get_summary_insight_data__(self, all_data):
        """
        returns summarized data from dataset
        """

                    # def load_yearly_data(year):
                    #     df = pd.DataFrame(requests.get(STATSAPI.format(year)).json()["statistics"])
                    #     df["DateTime"] = df["Timestamp"].str[:10] + "T12:00:00Z"
                    #     df["YearMonth"] = df["Timestamp"].str[:8] + "15"
                    #     df["Timestamp"] = pd.to_datetime(df["Timestamp"])
                    #     return df
                    #
                    # # tarb_api_url = "https://iabot.wmcloud.org/api.php?action=statistics&format=flat"
                    # # tarb_api_url = "https://iabot.wmcloud.org/api.php?action=statistics&format=flat"
                    # # https: // iabot.wmcloud.org / api.php?action = statistics & format = flat & only - year = 2025 & only - key = DeadEdits
                    #
                    # tarb_api_url = (
                    #     "https://iabot.wmcloud.org/api.php?"
                    #     f"action=statistics&format=flat"
                    # )
                    #
                    # r = requests.get(tarb_api_url)
                    # # TODO use a try/catch here
                    #
                    # if r.status_code != 200:
                    #     return None

        return {
            "test_value_1": 1,
            "test_value_2": 2,
            "test_value_3": 3,
        }




    def __get_raw_data_old(self):
        tarb_api_url = (
            "https://iabot.wmcloud.org/api.php?"
            f"action=statistics&format=flat"
        )

        try:
            r = requests.get(tarb_api_url)

            # do loop to get all years and concat

        except Exception as e:
            traceback.print_exc()
            return {"error": f"Problem accessing TARB stats ({str(e)})"}, 500

        if r.status_code != 200:
            raise TarbFetchError(f"Problem fetching raw TARB stats: Bad Request ({r.status_code})")

        return r.json()

