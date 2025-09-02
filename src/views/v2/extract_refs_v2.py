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
                # TODO somehow update page_errors if encountered
                #   maybe have __get_page_data__ access self.page_error?

            # Stop the timer and calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time

            self.page_data = {
                "iari_version": get_poetry_version("pyproject.toml"),
                "iari_command": "extract_refs",
                "page_errors": self.page_errors,
                "execution_time": f"{execution_time:.4f} seconds"
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

                    "section_names": page_data["section_names"],

                    "url_count": page_data["url_count"],
                    "urls": page_data["urls"],

                    "reference_count": page_data["reference_count"],
                    "references": page_data["references"],

                    "cite_refs_count": page_data["cite_refs_count"],
                    "cite_refs": page_data["cite_refs"],
            })

            # and return results
            return self.page_data, 200


        except MissingInformationError as e:
            traceback.print_exc()
            return jsonify(errors=[
                {
                    "error": type(e).__name__,
                    "details": str(e)
                },
            ]), 500

        except WikipediaApiFetchError as e:
            traceback.print_exc()
            return jsonify(errors=[
                {
                    "error": type(e).__name__,
                    "details": str(e)
                },
            ]), 500

        # except WikipediaApiFetchError as e:
        #     traceback.print_exc()
        #     return {
        #     "error": f"Wikipedia Api Fetch Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return jsonify(errors=[
                {
                    "error": type(e).__name__,
                    "details": str(e)
                },
            ]), 500

            # return {"error": f"{type(e)}: {str(e)}"}, 500


    def __get_page_data__(self):
        """
        set self.page_data:
            - if use_cache, retrieve from cache if possible, or
            - parse from self.job specs
        """

        page_spec = {
            "page_title": self.job.page_title,
            "domain": self.job.domain,
            "as_of": self.job.as_of,
            # TODO additional fields needed?:
            #   - timestamp of this information
            #   - maybe served from cache? what does cache mean now that we have databases?
        }


        self.analyzer = WikiAnalyzerV2()
        # for now, assumes page_spec is a wiki page.
        # In the future, we will be able to determine which analyzer to use based on media type
        # NB: each analyzer should "implement" a "base analyzer interface" to handle
        #  get_page_data(page_spec)
        #  page_spec should also be a formal object class, to allow polymorphic analyzers

        from src import app
        app.logger.debug(f"####")
        app.logger.debug(f"#### extract_refs_v2::__get_page_data__: right before returning results from analyzer.get_page_data")
        app.logger.debug(f"####")


        try:
            return self.analyzer.get_page_data(page_spec)

        except Exception as e:
            app.logger.error(f"analyzer.get_page_data: failed (got exception): {e}")
            return {
                "errors": [
                    {
                        "error": type(e).__name__,
                        "details": f"analyzer.get_page_data: failed (got exception): {e}",
                    }
                ]
            }
