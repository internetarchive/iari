from typing import Any, Optional, Tuple, List, Dict
import urllib.parse
import traceback
import time
import config
import requests

from src.models.wikimedia.enums import RequestMethods
from src.models.exceptions import MissingInformationError
from src.views.v2.statistics import StatisticsViewV2
from src.helpers.get_version import get_poetry_version

from src.models.v2.schema.refs_lookup_schema_v2 import RefsLookupSchemaV2
from src.models.v2.job.refs_lookup_job_v2 import RefsLookupJobV2
from src.constants.constants import OutputFormats


class RefsLookupV2(StatisticsViewV2):
    """
    returns reference data from citation database for page specified by job parameters
    """

    schema = RefsLookupSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: RefsLookupJobV2           # Holds usable variables, seeded from schema. Overrides StatisticsViewV2's "job"

    refs_data: Dict[str, Any] = {}  # holds references data

    def get(self):
        """
        entrypoint for GET refs_lookup endpoint
        must return a tuple: (Any, response_code)
        """
        return self.__process_request__(method=RequestMethods.get)

    def post(self):
        """
        entrypoint for POST refs_lookup endpoint
        must return a tuple: (Any,response_code)
        """
        return self.__process_request__(method=RequestMethods.post)

    def __process_request__(self, method=RequestMethods.post):  # default to POST

        from src import app
        app.logger.debug(f"==> RefsLookupV2::__process_request__({method})")

        # Start the timer
        start_time = time.time()

        try:

            # validate and setup params
            self.__validate_and_get_job__(method)  # inherited from StatisticsViewV2

            # get references from database
            results = self.__get_refs_data__()

            # Stop the timer and calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time

            self.page_data = {
                "iari_version": get_poetry_version("pyproject.toml"),
                "iari_command": "refs_lookup",
                "execution_time": f"{execution_time:.4f} seconds",
                "url": self.job.url,
                "use_raw": self.job.raw,
                "refs": results
            }

            # and return results
            return self.page_data, 200


        except MissingInformationError as e:
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"{type(e).__name__}: {str(e)}"}, 500


    def __get_refs_data__(self):
        """
        fetch all references from citations database matching criteria
        """

        # encoded_url = encodeURIComponent(self.job.url)
        encoded_url = urllib.parse.quote(self.job.url, safe='')
        use_raw = 'true' if self.job.raw else 'false'
        # 
        output = OutputFormats.get(self.job.output, {}).get('value', OutputFormats['JSON']['value'])  # 'unknown'

        citation_api_url = f"https://wikipediacitations.scatter.red/?url={encoded_url}&output={output}&raw={use_raw}"

        from src import app
        app.logger.debug(f"==> RefsLookupV2::__get_refs_data__: citation_api_url is: {citation_api_url}")

        headers = {"User-Agent": config.user_agent}
        response = requests.get(citation_api_url, headers=headers)

        # console.print(response.json())

        data = {}

        if response.status_code == 200:
            data = response.json()

        else:
            data = {
                'status': "NOT OK",
                'data': ["got bad response from json fetch for refs lookup"]
            }

        return data

            # raise WikipediaApiFetchError(
            #     f"Could not fetch page data. Got {response.status_code} from {wiki_fetch_url}"
            # )
