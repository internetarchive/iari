import logging
import time
import traceback

from typing import Any, Dict, Optional, List

from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.models.exceptions import MissingInformationError

from src.helpers.get_version import get_version_stamp

from src.views.v2.statistics import StatisticsViewV2
from src.models.v2.job.probe_job_v2 import ProbeJobV2
from src.models.v2.schema.probe_schema_v2 import ProbeSchemaV2

from src.constants.constants import ProbeMethod
from src.models.v2.probes.probe_test import ProbeTest
from src.models.v2.probes.probe_trust_project import ProbeTrustProject
from src.models.v2.probes.probe_verifyi import ProbeVerifyi



logger = logging.getLogger(__name__)


class ProbeV2(StatisticsViewV2):
    """
    Probes with various probing methods for a URL and returns results from probe
    """

    job: Optional[ProbeJobV2] = None
    schema: Schema = ProbeSchemaV2()

    url_link: str = ""
    probe_list: List[str] = []
    # data: Optional[Dict[str, Any]] = None


    def get(self):
        """
        main method of probe flask endpoint for flask.
        must return a tuple (Any,response_code)
        """
        from src import app
        app.logger.debug("==> ProbeV2")

        try:
            self.__validate_and_get_job__()
            if self.job:  # TODO what happens if self.job is not valid? why would it not be valid?
                self.url_link = self.job.unquoted_url
                self.probe_list = self.job.probe_list
                return self.__return_results__(self.url_link, self.probe_list)

        except MissingInformationError as e:
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500


    def __return_results__(self, url_link, probe_list):
        # Start the timer
        start_time = time.time()

        probe_results = self.__get_probe_results__(url_link, probe_list)
        probe_status = self.__get_probe_status__(probe_results)

        # Stop the timer and calculate execution time
        end_time = time.time()
        execution_time = end_time - start_time

        results = get_version_stamp()
        results.update({
            "execution_time": f"{execution_time:.4f} seconds",
            "url": url_link,
            "probes": probe_list,
            "probe_status": probe_status,
            "probe_results": probe_results
        })

        return results, 200


    @staticmethod
    def __get_probe_results__(url_link, probe_list):
        # error if probe list empty? or not...

        probe_results = {}

        for probe in probe_list:

            # add a keyed object to results as each probe is processed

            p_name = probe  # default value of probe is a string describing it's name

            try:
                # TEST method
                if p_name.upper() == ProbeMethod.TEST.value:
                    results = ProbeTest.probe(url=url_link)

                # VERIFYI method
                elif p_name.upper() == ProbeMethod.VERIFYI.value:
                    results = ProbeVerifyi.probe(url=url_link)

                # TRUST_PROJECT method
                elif p_name.upper() == ProbeMethod.TRUST_PROJECT.value:
                    results = ProbeTrustProject.probe(url=url_link)

                # probe method not supported
                else:
                    results = {
                        "errors": [
                            f"Unknown probe: {p_name}"
                        ]
                    }

                # add this method's results to accumulated list
                probe_results[p_name] = results

            except Exception as e:
                traceback.print_exc()
                probe_results[p_name] = {
                    "error": f"Error while probing {p_name}",
                    "error_details": str(e)
                }

        return probe_results



    @staticmethod
    def __get_probe_status__(probe_results):
        """
        evaluates probe_results and returns a single metric
        """
        probe_status = ""
        for probe_key, probe_value in probe_results.items():

            # must append probe_status based on evaluation
            # of probe_value, which is specific to each key.
            # similar switching as in __get_probe_results__
            pass

        probe_status = "TBD"  # for now....
        return probe_status
