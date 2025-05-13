import logging
import time
import traceback

from typing import Any, Dict, Optional, List

from flask import request
from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.models.exceptions import MissingInformationError, UnknownValueError

from src.helpers.get_version import get_version_stamp
from src.helpers.probe_utils import ProbeUtils

from src.views.v2.statistics import StatisticsViewV2
from src.models.v2.job.probe_job_v2 import ProbeJobV2
from src.models.v2.schema.probe_schema_v2 import ProbeSchemaV2




logger = logging.getLogger(__name__)


class ProbeV2(StatisticsViewV2):
    """
    Probes with various probing methods for a URL and returns results from probe
    """

    job: Optional[ProbeJobV2] = None
    schema: Schema = ProbeSchemaV2()

    url_link: str = ""
    probe_list: List[str] = []
    refresh: Optional[bool] = False

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
                self.refresh = self.job.refresh
                # self.refresh = False
                return self.__return_results__()

        except MissingInformationError as e:
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500


        except UnknownValueError as e:
            traceback.print_exc()
            return {"error": f"Unknown Value Error: {str(e)}"}, 500


        except Exception as e:
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500


    def __return_results__(self):

        start_time = time.time()

        probe_results = ProbeUtils.get_probe_results(self.url_link, self.probe_list, self.refresh)

        execution_time = time.time() - start_time  # elapsed = now - then

        results = get_version_stamp("probe", request.endpoint)
        results.update({
                "execution_time": f"{execution_time:.4f} seconds",
                "url": self.url_link,
                "probe_list": self.probe_list,
                "probe_results": probe_results
        })
        if self.job.tag:
            results.update({"tag": self.job.tag})

        return results, 200

