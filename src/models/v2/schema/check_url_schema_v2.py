import logging

from marshmallow import post_load
from marshmallow.fields import Bool, Int, String
from src.models.api.schema.refresh import BaseSchema

from src.models.v2.job.check_url_job_v2 import CheckUrlJobV2

logger = logging.getLogger(__name__)


class CheckUrlSchemaV2(BaseSchema):
    """This validates the patron input in the get request"""

    url = String(required=True)
    method = String(required=False)
    timeout = Int(required=False)

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> CheckUrlJobV2:  # type: ignore # dead: disable
        """Return job object as schema return value"""

        job = CheckUrlJobV2(**data)
        job.validate_fields()

        return job
