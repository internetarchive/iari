from typing import Any, Optional, Tuple, List, Dict
import traceback
import time
from flask import jsonify

from src.models.exceptions import MissingInformationError
from src.constants.constants import RequestMethods
from src.helpers.get_version import get_poetry_version
from src.helpers.iari_utils import iari_errors

from src.views.v2.statistics import StatisticsViewV2
from src.models.v2.analyzers.grok_analyzer import GrokAnalyzerV2

from src.models.v2.schema.extract_grok_schema_v2 import ExtractGrokSchemaV2
from src.models.v2.job.extract_grok_job_v2 import ExtractGrokJobV2


class ExtractGrokV2(StatisticsViewV2):
    """
    returns citation data for page specified by parameters in job.
    """

    schema = ExtractGrokSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: ExtractGrokJobV2           # Holds usable variables, seeded from schema. Overrides StatisticsViewV2's "job"

    refresh: Optional[bool] = False

    # analyzer: IariAnalyzer  # TODO make analyzer instance variable

    return_data: Dict[str, Any] = {}  # holds parsed data from page processing
    # NB TODO page_data should be explicit type, returned by analyzer

    page_errors: List[Dict[str, Any]] = None

    def get(self):
        """
        the GET entrypoint for extract_refs
        must return a tuple: (Any, response_code)
        """
        return self.__process_request__(method=RequestMethods.get)

    def post(self):
        """
        the POST entrypoint for extract_refs
        must return a tuple: (Any, response_code)
        """
        return self.__process_request__(method=RequestMethods.post)

    def __process_request__(self, method=RequestMethods.post):

        from src import app
        app.logger.debug(f"==> ExtractGroksV2::__process_request__({method})")

        # Start the timer
        start_time = time.time()

        try:

            # validate and setup params
            self.__validate_and_get_job__(method)  # inherited from StatisticsViewV2

            # get page_data, either from cache or newly calculated
            app.logger.debug(f"==> ExtractGroksV2::start page_data")

            page_data = self.__get_page_data__()

            # Stop the timer and calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time

            # set page_errors if any:
            if page_data.get("error"):
                self.page_errors = [page_data.get("error")]


            # initialize return_data fields
            self.return_data = {
                "iari_version": get_poetry_version("pyproject.toml"),
                "iari_command": "extract_grok",
                "page_errors": self.page_errors,
                "execution_time": f"{execution_time:.4f} seconds",
            }

            # only include hydrate field if hydrate is true
            if self.job.hydrate:
                self.return_data["hydrate"] = self.job.hydrate

            # only include use_local_hash if provided
            if self.job.use_local_cache is not None :
                self.return_data["use_local_cache"] = True

            # pick and choose which fields from page_data we want to pass on to response
            self.return_data.update(
                {
                    "media_type": page_data.get("media_type"),
                    "page_title": page_data.get("page_title"),
                    # here are all the statistical data extracted from the page...
                    "url_count": page_data.get("url_count"),
                    "urls": page_data.get("urls"),
            })

            # return results
            return self.return_data, 200


        except MissingInformationError as e:
            app.logger.debug(f"ExtractGrokV2::__process_request__ MissingInformationError {e}")
            traceback.print_exc()
            return iari_errors(e), 500

        except Exception as e:
            app.logger.debug(f"ExtractGrokV2::__process_request__ Exception {e}")
            traceback.print_exc()
            return iari_errors(e), 500


    def __get_page_data__(self):
        """
        returns the page data or
        errors structure:
        {
            "errors": [
                {
                    "error": type(e).__name__,
                    "details": f"analyzer.get_page_data: Error: {e}",
                }
            ]
        }
        """

        page_spec = {
            "page_title": self.job.page_title,
            "use_local_cache": self.job.use_local_cache,
            # TODO additional fields needed?:
            #   - timestamp of this information
        }

        self.analyzer = GrokAnalyzerV2()  # For now, assume page_spec refers to a grok page.

        from src import app
        app.logger.debug(f"==> ExtractGrokV2::__get_page_data__: start analyzer.extract_page_data")

        try:
            return self.analyzer.extract_page_data(page_spec)

        except Exception as e:
            app.logger.error(f"ExtractGrokV2::__get_page_data__ Exception {e}")
            traceback.print_exc()
            return {
                # NB: could add identifying information here
                "error": f"{type(e).__name__}: {str(e)}"
            }

