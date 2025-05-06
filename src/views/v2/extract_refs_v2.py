from typing import Any, Optional, Tuple, List, Dict
import traceback
import time

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
        entrypoint for GET extract_refs endpoint
        must return a tuple: (Any, response_code)
        """
        return self.__process_request__(method=RequestMethods.get)

    def post(self):
        """
        entrypoint for POST extract_refs endpoint
        must return a tuple: (Any,response_code)
        """
        return self.__process_request__(method=RequestMethods.post)

    def __process_request__(self, method=RequestMethods.post):  # default to POST

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
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"{type(e).__name__}: {str(e)}"}, 500


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

        return self.analyzer.get_page_data(page_spec)


    # TODO: delete this!!!
    #  def __get_page_results(self, url_link: str, probe_list: list, refresh: bool = False):
    #     """
    #     returns overall truth score and probe results for url_link for each probe in probe_list
    #     returns { score: <xxx>, probe_results{ a: <xxx>, b: <xxx>, c: <xxx> }
    #
    #     TODO: error if probe list empty? or not...
    #
    #     """
    #
    #     from src import app
    #     app.logger.debug(f"==> get_probe_results: url_link: {url_link}, probe_list: {probe_list}, refresh = {str(refresh)}")
    #
    #     probe_results = {}
    #
    #     if refresh:
    #         """
    #         if refresh:
    #             (fetch all probes anew, and save new data in cache for url and probe)
    #             for p in probe_list
    #                 fetch p(url)
    #                 save in cache p-url
    #         """
    #
    #         # fetch all probes anew, and save new data in cache for url/probe combo
    #         for p in probe_list:
    #             new_data = ProbeUtils.get_probe_data(url_link, p)
    #             probe_results[p] = new_data
    #
    #             # TODO NB what to do if new_data is error?
    #             #   may want to keep cache as is if already there,
    #             #   and "send back" error as response
    #             #   basically, not save to cache if error
    #
    #             # TODO have some way of tagging probe data with a timestamp of access date
    #
    #             set_cache(url_link, CacheType.probes, p, new_data)
    #
    #     else:
    #         """
    #         if not refresh:
    #             for p in probe_list
    #                 if is_cached, do nothing, as cache already exists fpr p-url
    #                 if not is_cached
    #                     fetch p(url)
    #                     set_cache p-url
    #         """
    #         for p in probe_list:
    #             if not is_cached(url_link, CacheType.probes, p):
    #                 new_data = ProbeUtils.get_probe_data(url_link, p)
    #                 probe_results[p] = new_data
    #
    #                 # TODO NB what to do if new_data is error?
    #                 #
    #                 # do not save errors in cache!
    #                 #
    #                 # IDEA: set_cache can behave like a "store another snapshot". This will give us a way
    #                 #   to have a sort of database of cached fetches, to have a hotory
    #                 #   we probably should have a comparison so we dont resave same data, but should
    #                 #   at least save a "snapshot" date if multiple fetches produce same results
    #
    #                 set_cache(url_link, CacheType.probes, p, new_data)
    #
    #             else:  # data for probe p is cached, so use it
    #                 new_data = get_cache(url_link, CacheType.probes, p)
    #                 probe_results[p] = new_data
