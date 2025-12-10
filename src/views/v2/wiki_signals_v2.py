from typing import Any, Optional, Tuple, List, Dict
import config
import traceback
import time
import datetime
import numpy as np
import pandas as pd
import pickle

import requests
from bs4 import BeautifulSoup, NavigableString
from flask import request

from src.helpers.get_version import get_poetry_version

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError, TarbFetchError, IariFetchError
from src.constants.constants import RequestMethods
from src.views.v2.statistics import StatisticsViewV2

from src.models.v2.job.wiki_signals_job_v2 import WikiSignalsJobV2
from src.models.v2.schema.wiki_signals_schema_v2 import WikiSignalsSchemaV2

from src.helpers.signal_utils import get_signal_data_for_domain

SIGNALS_CACHE_DIR = f"{config.iari_cache_dir}cache"
# SIGNALS_CSV = f"data/CredibilityIndicators_PerennialSources_MBFC_20250919.csv"
SIGNALS_CSV = config.iari_cache_dir

class WikiSignalsV2(StatisticsViewV2):
    """
    returns wiki signal data

    inputs: domain
    (example inputs: https://en.wikipedia.org/wiki/Main_Page, en.wikipedia.org, wikipedia.org, wikimediafoundation.org)
    (??? do we want url or domain? one or the other?)
    (domain will be extracted from domain if it looks a url)
    """

    schema = WikiSignalsSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: WikiSignalsJobV2  # Holds usable variables, seeded from schema. Overrides StatisticsViewV2's "job"

    return_data: Dict[str, Any] = {}  # holds processed data from wiki signal extracting

    def get(self):
        """
        flask entrypoint for GET
        must return a tuple: (Any, response_code)
        """
        from src import app
        app.logger.debug(f"==> WikiSignalV2::get")

        return self.__process_request__(method=RequestMethods.get)

    def __process_request__(self, method=RequestMethods.post):  # default to POST method

        from src import app
        app.logger.debug(f"==> WikiSignalV2::__process_request__, method = {method}")

        # Start the timer
        start_time = time.time()

        # fetch the insight data
        try:

            # validate and setup params
            self.__validate_and_get_job__(method)  # inherited/subclassed from StatisticsViewV2

            # fetch the data, parse and return summary
            signal_data = self.__get_signal_data__()

            # Stop the timer and calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time

            # seed the return data with the job params
            self.return_data = {
                "iari_version": get_poetry_version("pyproject.toml"),
                "iari_command": "wiki_signals",
                "endpoint": request.endpoint,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "execution_time": f"{execution_time:.4f} seconds",
            }

            # and append the insight data we really want!
            self.return_data.update(signal_data)

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

    def __get_signal_data__(self):
        """
        retrieve signal data for domain and return it
        returns: dict of summary data
        """

        # load signal data if not there already


        # just do one domain for now...

        try:
            signal_data = self.__get_domain_signal_data__()
        except Exception as e:
            raise TarbFetchError(f"Problem getting Wiki Signal data ({str(e)})")

        from src import app
        app.logger.debug(f"==> signal_data: {signal_data}")

        return {
            # "raw_data": raw_data,
            "domains": {
                self.job.domain : signal_data,
            }
        }

    def __get_domain_signal_data__(self):

        signals = get_signal_data_for_domain(domain=self.job.domain, force_refresh=False)

        return {
            "debug": {
                "domain": self.job.domain,
            },
            "synopsis": f"Signal data for {self.job.domain}",
            "signals": signals
        }
