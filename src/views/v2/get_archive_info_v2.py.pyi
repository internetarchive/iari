from typing import Any, Optional, Tuple, List, Dict
import urllib.parse
import traceback
import time
import config
import requests

from src.constants.constants import RequestMethods
from src.models.exceptions import MissingInformationError
from src.views.v2.statistics import StatisticsViewV2
from src.helpers.get_version import get_poetry_version

from src.models.v2.schema.get_archive_info_schema_v2 import GetArchiveInfoSchema
from src.models.v2.job.get_archive_info_job_v2 import GetArchiveInfoJobV2


class GetArchiveInfoV2(StatisticsViewV2):
    """
    returns reference data from citation database for page specified by job parameters
    """

    schema = GetArchiveInfoSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: GetArchiveInfoJobV2           # Holds usable variables, seeded from schema.
                                       # NB: Overrides StatisticsViewV2's "job"

    archive_data: Dict[str, Any] = {}

    def get(self):
        """
        entrypoint for GET get_archive_data endpoint
        must return a tuple: (Any, response_code)
        """
        return self.__process_request__(method=RequestMethods.get)

    def post(self):
        """
        entrypoint for POST get_archive_data endpoint
        must return a tuple: (Any,response_code)
        """
        return self.__process_request__(method=RequestMethods.post)

    def __process_request__(self, method=RequestMethods.post):

        from src import app
        app.logger.debug(f"==> GetArchiveInfoV2::__process_request__({method})")

        # Start the timer
        start_time = time.time()

        try:

            # validate and setup params
            self.__validate_and_get_job__(method)
            # inherited from StatisticsViewV2

            # get archive info from wayback API
            results = self.__get_archive_info__()

            # Stop the timer and calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time

            self.archive_data = {
                "iari_version": get_poetry_version("pyproject.toml"),
                "iari_command": "get_archive_info",
                "execution_time": f"{execution_time:.4f} seconds",
                "url": self.job.url,
                "archives": results
            }

            # and return results
            return self.page_data, 200


        except MissingInformationError as e:
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"{type(e).__name__}: {str(e)}"}, 500


    def __get_archive_data__(self):
        """
        fetch all archie info for reference/link/citation/claim?
        from citations database matching criteria
        """


        #
        ##
        ###
        #   this is where we fetch the archive data from the wayback machine.
        ###
        ##
        #

        encoded_url = urllib.parse.quote(self.job.url, safe='')

        # # set all local variables specified by params here
        # use_feature = 'true' if self.job.feature else 'false'

        wayback_cdx_endpoint = "https://web.archive.org/cdx/search/cdx"
        params = {
            "url": url,
            "output": "json",
            "fl": "timestamp,original,statuscode"
        }
        resp = requests.get(cdx_endpoint, params=params).json()

        results = []
        for row in resp[1:]:  # first row is header
            results.append({
                "url": row[0],
                "timestamp": row[1],
                "status": row[2],
            })

        if response.status_code == 200:
            data = response.json()
            # we can process the data here
        else:
            data = {
                'status': "NOT OK",
                'data': ["got bad response from json fetch for refs lookup"]
            }

        return data
