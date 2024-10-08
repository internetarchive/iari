from typing import Any, Optional, Tuple, List, Dict
import traceback
import time

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.wikimedia.enums import RequestMethods
from src.models.v2.schema.extract_refs_schema_v2 import ExtractRefsSchemaV2
from src.models.v2.job.extract_refs_job_v2 import ExtractRefsJobV2

from src.views.v2.statistics import StatisticsViewV2
from src.models.v2.analyzers.wiki_analyzer import WikiAnalyzerV2

from src.helpers.get_version import get_poetry_version


class ExtractRefsV2(StatisticsViewV2):

    """
    takes an array of page specifiers, and
    returns data for all citations for each page.
    """

    schema = ExtractRefsSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: ExtractRefsJobV2           # Holds usable variables, seeded from schema. Overrides StatisticsViewV2's "job"

    # analyzer: IariAnalyzer  # TODO make analyzer variable

    page_data: Dict[str, Any] = {}  # holds parsed data from page processing
    # NB TODO page_data should be explicit type, returned by analyzer

    page_errors: List[Dict[str, Any]] = None

    def get(self):
        """
        flask GET entrypoint for returning extract_refs results
        must return a tuple: (Any, response_code)
        """
        from src import app
        app.logger.debug(f"==> ExtractRefsV2::get")

        return self.__process_request__(method=RequestMethods.get)

    def post(self):
        """
        flask POST entrypoint for returning fetchrefs results
        must return a tuple: (Any,response_code)
        """
        from src import app
        app.logger.debug(f"==> ExtractRefsV2::post")

        return self.__process_request__(method=RequestMethods.post)


    def __process_request__(self, method=RequestMethods.post):  # default to POST

        from src import app
        app.logger.debug(f"==> ExtractRefsV2::__process_request__, method = {method}")

        # Start the timer
        start_time = time.time()

        try:

            # validate and setup params
            self.__validate_and_get_job__(method)  # inherited from StatisticsViewV2

            # process page specified by job data and save in returned page_data
            # TODO get cached data here if possible
            # TODO somehow update page_errors if encountered
            #   maybe have __get_page_data__ access self.page_error?
            page_data = self.__get_page_data__()

            # Stop the timer and calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time
            #         timestamp = datetime.timestamp(datetime.utcnow())
            #         isodate = datetime.isoformat(datetime.utcnow())

            self.page_data = {
                "iari_version": get_poetry_version("pyproject.toml"),
                "iari_command": "extract_refs",
                "page_errors": self.page_errors,
                "execution_time": f"{execution_time:.4f} seconds"
            }

            self.page_data.update(
                {
                    "media_type": page_data["media_type"],
                    "page_title": page_data["page_title"],
                    "domain": page_data["domain"],
                    "as_of": page_data["as_of"],
                    "page_id": page_data["page_id"],
                    "revision_id": page_data["revision_id"],
                    "reference_count": page_data["reference_count"],
                    "references": page_data["references"],
                }
            )

            # and return results
            return self.page_data, 200


        except MissingInformationError as e:
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500

    def __get_page_data__(self):
        """
        parses page specified by self.job and sets self.page_data to object of parsed values
        """

        page_spec = {
            "page_title": self.job.page_title,
            "domain": self.job.domain,
            "as_of": self.job.as_of,
        }

        # TODO added fields needed:
        # timestamp of this information
        # maybe served from cache? what does cache mean now that we have databases?

        # for now, assumes page_spec is a wiki page.
        # In the future, we will be able to determine which analyzer to use based on media type
        # NB: each analyzer should "implement" a base to handle get_page_data(page_spec
        #   page_spec should, then, also be a formal object class, to allow polymorphisms of analyzers
        self.analyzer = WikiAnalyzerV2()

        return self.analyzer.get_page_data(page_spec)
