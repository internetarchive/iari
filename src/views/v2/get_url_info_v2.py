import logging
import time
import traceback
from typing import Any, Dict, Optional, List

from flask import request
from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.helpers.get_version import get_version_stamp
from src.helpers.probe_utils import ProbeUtils

from src.models.exceptions import MissingInformationError, UnknownValueError

from src.views.v2.statistics import StatisticsViewV2
from src.helpers.get_version import get_version_stamp

from src.constants.constants import UrlInfoParts
from src.models.v2.job.get_url_info_job_v2 import GetUrlInfoJobV2
from src.models.v2.schema.get_url_info_schema_v2 import GetUrlInfoSchemaV2

# from src.helpers.probe_utils import ProbeUtils


logger = logging.getLogger(__name__)


class GetUrlInfoV2(StatisticsViewV2):
    """
    returns info for a URL
    may return status info, probe info, and more
    specifies "parts" to return, "status|probe" being default
    respects "refresh" as to whether to refresh cache or not for parts
    """

    job: Optional[GetUrlInfoJobV2] = None
    schema: Schema = GetUrlInfoSchemaV2()

    url_link: str = ""
    parts_list: List[str] = []
    probe_list: List[str] = []
    refresh: Optional[bool] = False

    def get(self):
        """
        main method of flask get endpoint .
        """
        from src import app
        app.logger.debug("==> GetUrlInfoV2")

        try:
            self.__validate_and_get_job__()
            if self.job:
                # TODO what happens if self.job is not valid?
                #  why would it not be valid?
                self.url_link = self.job.unquoted_url
                self.parts_list = self.job.parts_list
                self.refresh = self.job.refresh
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

        parts = self.__get_parts__(self.parts_list)

        execution_time = time.time() - start_time  # elapsed = now - then

        results = get_version_stamp("get_url_info", request.endpoint)
        results.update({
                "execution_time": f"{execution_time:.4f} seconds",
                "url": self.url_link,
                "parts_list": self.parts_list,
                "probe_list": self.probe_list,
                "parts": parts
        })

        return results, 200


    def __get_parts__(self, parts_list):  # this may become part of UrlUtils

        results = {}

        # get parts
        for part in parts_list:

            part_name = ""

            try:
                # status
                if part.upper() == UrlInfoParts.STATUS.value:
                    part_name = "status"
                    # results = GetUrlStatus(url=url)
                    results[part] = {"part_name": part_name }

                # probe
                elif part.upper() == UrlInfoParts.PROBES.value:
                    part_name = "probes"
                    # results = (url=url)
                    results[part] = {"part_name": part_name }

                # probe method not supported
                else:
                    results[part] = {
                        "errors": [
                            f"Unknown part: {part}"
                        ]
                    }

            except Exception as e:
                results[part] = {
                    "errors": [
                        f"Error while fetching part {part} ({str(e)})."
                    ]
                }

        return results

