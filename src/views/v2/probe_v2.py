import logging
import traceback

from datetime import datetime
from typing import Any, Dict, Optional, List

from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.models.exceptions import MissingInformationError

from src.helpers.get_version import get_version_stamp

from src.models.v2.job.probe_job_v2 import ProbeJobV2
from src.models.v2.probes.probe_test import ProbeTest
from src.models.v2.probes.probe_trust_project import ProbeTrustProject
from src.models.v2.probes.probe_verifyi import ProbeVerifyi
from src.models.v2.schema.probe_schema_v2 import ProbeSchemaV2
from src.views.v2.statistics import StatisticsViewV2

from src.constants.constants import ProbeMethod


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
        app.logger.debug("ProbeV2: running")

        # self.__validate_and_get_job__()
        # if self.job:
        #     return self.__return_probe_results__()

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
        results = get_version_stamp()
        results.update({
            "url": url_link,
            "probes": probe_list,
            "probe_results": self.__get_probe_results__(url_link, probe_list)
        })
        return results, 200


    @staticmethod
    def __get_probe_results__(url_link, probe_list):
        # error if probe list empty? or not...

        all_results = {}

        for probe in probe_list:

            # amend all_results as each probe in list is processed

            p_name = probe.upper()

            try:
                if p_name == ProbeMethod.TEST.value:
                    results = ProbeTest.probe(url=url_link)

                elif p_name == ProbeMethod.VERIFYI.value:
                    results = ProbeVerifyi.probe(url=url_link)

                elif p_name == ProbeMethod.TRUST_PROJECT.value:
                    results = ProbeTrustProject.probe(url=url_link)

                else:  # probe not found
                    results = {"error": f"Unknown probe: {p_name}"}

                all_results[p_name] = results

            except Exception as e:
                traceback.print_exc()
                all_results[p_name] = {
                    "error": f"Error while probing {p_name}",
                    "error_details": str(e)
                }

        return all_results
