import time
import traceback

from datetime import datetime
from typing import Any, Dict, Optional, List

from flask import request
from flask_restful import Resource, abort  # type: ignore
from marshmallow import Schema

from src.models.exceptions import MissingInformationError, UnknownValueError

from src.helpers.get_version import get_poetry_version, get_version_stamp
from src.helpers.signal_utils import get_signal_data_for_url, get_signal_data_for_domain

from src.views.v2.statistics import StatisticsViewV2

from src.models.v2.job.signals_job_v2 import SignalsJobV2
from src.models.v2.schema.signals_schema_v2 import SignalsSchemaV2

class SignalsV2(StatisticsViewV2):
    """
    return signal data associated with url (the domain of the url)
    """

    job: Optional[SignalsJobV2] = None
    schema: Schema = SignalsSchemaV2()

    url_link: str = ""
    domain: str = ""

    refresh: Optional[bool] = False

    # data: Optional[Dict[str, Any]] = None


    def get(self):
        """
        must return a tuple (Any,response_code)
        """
        from src import app
        app.logger.debug("==> SignalsV2")

        try:
            self.__validate_and_get_job__()
            if self.job:  # TODO what happens if self.job is not valid? why would it not be valid?

                self.url_link = self.job.unquoted_url
                self.domain = self.job.domain
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

        now = datetime.utcnow()
        start_time = time.time()

        results = {
            "iari_version": get_poetry_version("pyproject.toml"),
            "iari_command": "signals",
            "endpoint": request.endpoint,
            "timestamp": int(datetime.timestamp(now)),
            "isodate": now.isoformat(),
        }
        if self.job.tag:
            results.update({"tag": self.job.tag})

        # signals_results = get_signal_data_for_url_old(self.url_link, self.refresh)
        signals_results = get_signal_data_for_domain(self.domain, self.refresh)
        execution_time = time.time() - start_time  # elapsed = now - then

        results.update({
            "execution_time": f"{execution_time:.4f} seconds",
            "url": self.url_link,
            "domain": self.job.domain,
            "signal_data": signals_results
        })

        return results, 200

