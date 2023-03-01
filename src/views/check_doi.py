from typing import Any, Dict

from src.models.api.check_doi.check_doi_schema import CheckDoiSchema
from src.models.api.job.check_doi_job import CheckDoiJob
from src.views.statistics import StatisticsView


class CheckDoi(StatisticsView):
    """
    This models all action based on requests from the frontend/patron
    It is instantiated at every request

    This view does not contain any of the checking logic.
    See src/models/checking
    """

    job: CheckDoiJob
    schema: CheckDoiSchema()
    serving_from_json: bool = False
    headers: Dict[str, Any] = {
        "Access-Control-Allow-Origin": "*",
    }
    data: Dict[str, Any] = {}
    # todo implement
    raise NotImplementedError()
