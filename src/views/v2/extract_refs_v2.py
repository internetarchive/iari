from typing import Any, Optional, Tuple, List, Dict
import traceback
import time
from flask import jsonify

from src import WikipediaApiFetchError
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.enums import RequestMethods

from src.models.v2.schema.extract_refs_schema_v2 import ExtractRefsSchemaV2
from src.models.v2.job.extract_refs_job_v2 import ExtractRefsJobV2

from src.views.v2.statistics import StatisticsViewV2

# the analyzer object that
from src.models.v2.analyzers.wiki_analyzer import WikiAnalyzerV2

from src.helpers.get_version import get_poetry_version
from src.helpers.iari_utils import iari_errors


class ExtractRefsV2(StatisticsViewV2):
    """
    returns citation data for page specified by parameters in job.
    """

    schema = ExtractRefsSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: ExtractRefsJobV2           # Holds usable variables, seeded from schema. Overrides StatisticsViewV2's "job"

    refresh: Optional[bool] = False

    # analyzer: IariAnalyzer  # TODO make analyzer instance variable

    page_data: Dict[str, Any] = {}  # holds parsed data from page processing
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
        app.logger.debug(f"==> ExtractRefsV2::__process_request__({method})")

        # Start the timer
        start_time = time.time()

        try:

            # validate and setup params
            self.__validate_and_get_job__(method)  # inherited from StatisticsViewV2

            # get page_data, either from cache or newly calculated
            page_data = self.__get_page_data__()
                # TODO get cached data here if possible
                # TODO somehow access self.page_errors here
                #   self.page_errors should collect errors encountered while processing the page,
                #       but not erroneous enough to fail processing
                #   maybe have __get_page_data__ access/append self.page_errors?

            # Stop the timer and calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time

            # initialize page_data fields
            self.page_data = {
                "iari_version": get_poetry_version("pyproject.toml"),
                "iari_command": "extract_refs",
                "page_errors": self.page_errors,
                "execution_time": f"{execution_time:.4f} seconds",
                "hydrate": self.job.hydrate,
            }

            # pick and choose which fields from page_data we want to pass on to response
            self.page_data.update(
                {
                    "media_type": page_data["media_type"],
                    "page_title": page_data["page_title"],
                    "domain": page_data["domain"],
                    "as_of": page_data["as_of"],
                    "page_id": page_data["page_id"],
                    "revision_id": page_data["revision_id"],

                    # here is all the specific statistical data fetched from article...

                    "section_names": page_data["section_names"],

                    "url_count": page_data["url_count"],
                    "urls": page_data["urls"],

                    "reference_count": page_data["reference_count"],
                    "references": page_data["references"],

                    "cite_refs_count": page_data["cite_refs_count"],
                    "cite_refs": page_data["cite_refs"],
            })

            # return results
            return self.page_data, 200


        except MissingInformationError as e:
            app.logger.debug(f"ExtractRefsV2::__process_request__ MissingInformationError {e}")
            traceback.print_exc()
            return iari_errors(e), 500

        except WikipediaApiFetchError as e:
            app.logger.debug(f"ExtractRefsV2::__process_request__ WikipediaApiFetchError {e}")
            traceback.print_exc()
            return iari_errors(e), 500

        except Exception as e:
            app.logger.debug(f"ExtractRefsV2::__process_request__ Exception {e}")
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

        set self.page_data:
            - if self.use_cache,
                - retrieve from cache if exists
            - if not self.use_cache or cache not exist
                - parse from self.job specs
        """

        page_spec = {
            "page_title": self.job.page_title,
            "domain": self.job.domain,
            "as_of": self.job.as_of,
            "hydrate": self.job.hydrate,
            # TODO additional fields needed?:
            #   - timestamp of this information
            #   - maybe served from cache? what does cache mean now that we have databases?
        }

        self.analyzer = WikiAnalyzerV2()
        # For now, assume page_spec refers to a wiki page.
        # TODO In the future, determine which analyzer to use based on media type.
        #   - or, have a generic analyzer that delegates a specific analyzer based on page_spec
        # NB: each analyzer should implement a "base analyzer" interface that should include:
        #  get_page_data(page_spec)
        #   - page_spec should also be a formal object class, with default required fields.
        #   - page_spec should be a property of the analyzer class object instance
        #   - This will allow analyzers to be polymorphic, wherein they could process amy type of page/media

        return self.analyzer.get_page_data(page_spec)

