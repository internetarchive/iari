from typing import Any, Optional, Tuple, List, Dict
import config
import traceback
import time
import datetime
import pandas as pd
import pickle

import requests
from bs4 import BeautifulSoup, NavigableString
from flask import request

from src.helpers.get_version import get_poetry_version

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError, TarbFetchError
from src.constants.constants import RequestMethods
from src.views.v2.statistics import StatisticsViewV2

from src.models.v2.job.insights_tarb_job_v2 import InsightsTarbJobV2
from src.models.v2.schema.insights_tarb_schema_v2 import InsightsTarbSchemaV2

TARB_CACHE_DIR = f"{config.iari_cache_dir}cache"
STATSAPI_ONLYYEAR = "https://iabot.wmcloud.org/api.php?action=statistics&format=flat&only-year={}"
# TODO may want to decorate api url with filtering out fields to reduce file size over the wire
# STRYEAR = 2016
STRYEAR = 2022
ENDYEAR = datetime.date.today().year


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


        # TODO ??? should we set self.execution_errors here?

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
        """
        retrieve raw data and summarize it
        returns: dict of summary data

        TODO Shall we set self.execution_errors here rather than raise error?
            or, we could set self.execution_errors when exception caught
        """
        try:
            raw_data = self.__get_raw_insight_data__()
        except Exception as e:
            raise TarbFetchError(f"Problem getting raw TARB stats ({str(e)})")

        try:
            summary_data = self.__get_summary_insight_data__(raw_data)
        except Exception as e:
            raise TarbFetchError(f"Problem summarizing TARB stats ({str(e)})")

        from src import app
        app.logger.debug(f"==> summary_data: {summary_data}")

        return {
            # "raw_data": raw_data,
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

        def load_yearly_data(year, force_refresh=False):
            # pull from cache if there...
            import os
            os.makedirs(TARB_CACHE_DIR, exist_ok=True)
            cache_path = os.path.join(TARB_CACHE_DIR, f"stats_{year}.pickle")

            from src import app
            app.logger.debug(f"==> load_yearly_data:: cache_path is {cache_path}, force_refresh = {force_refresh}")

            # ✅ Step 1: Load from cache if exists and not forcing refresh
            if not force_refresh and os.path.exists(cache_path):
                app.logger.debug(f"Loading {year} from cache...")
                with open(cache_path, "rb") as f:
                    return pickle.load(f)
                    ### return pd.read_parquet(cache_path)

            # ✅ Step 2: Fetch from API if not cached
            app.logger.debug(f"Fetching {year} from API...")
            response = requests.get(STATSAPI_ONLYYEAR.format(year))
            response.raise_for_status()
            data = response.json()["statistics"]

            df = pd.DataFrame(data)
            df["DateTime"] = df["Timestamp"].str[:10] + "T12:00:00Z"
            df["YearMonth"] = df["Timestamp"].str[:8] + "15"
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", utc=True)

            # ✅ Step 3: Cache to disk
            with open(cache_path, "wb") as f:
                pickle.dump(df, f)
            return df

        def load_data():
            return pd.concat([load_yearly_data(y, force_refresh=False) for y in range(STRYEAR, ENDYEAR)] + [load_yearly_data(ENDYEAR, force_refresh=True)])

        try:
            df_all_data = load_data()

        except Exception as e:
            raise TarbFetchError(f"Problem fetching raw TARB stats: ({str(e)})")

        # return df_all_data.to_dict("records")
        return df_all_data


    def __get_summary_insight_data__(self, df_all_data):
        """
        returns summarized data from dataset
        """
        fday = df_all_data["Timestamp"].dt.date.min()
        lday = df_all_data["Timestamp"].dt.date.max()

        return {
            "first_day": fday.isoformat(),  # JSON safe
            "last_day": lday.isoformat(),   # JSON safe
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

