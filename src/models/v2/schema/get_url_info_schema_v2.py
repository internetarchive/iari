import logging

from marshmallow import post_load
from marshmallow.fields import Bool, Int, String
from src.models.api.schema.refresh import BaseSchema

from src.models.v2.job.get_url_info_job_v2 import GetUrlInfoJobV2

logger = logging.getLogger(__name__)


class GetUrlInfoSchemaV2(BaseSchema):
    """This validates the patron input in the get request"""

    url = String(required=True)

    parts = String(required=False)  # defaults to none, which means ALL; ex. "status|probes"
    status_method = String(required=False)
    probes = String(required=False)  # e.g. "verifyi|iffy"

    timeout = Int(required=False)

    # noinspection PyUnusedLocal
    @post_load
    # NB: **kwargs is needed here despite what the validator claims
    def post_load_function(self, data, **kwargs) -> GetUrlInfoJobV2:  # type: ignore # dead: disable
        """
        Returns job object as GetUrlInfoSchemaV2 return value (rather than
        default object associated with this getUrlInfoSchemaV2 class?)
        """

        job = GetUrlInfoJobV2(**data)
        job.validate_fields()

        return job
