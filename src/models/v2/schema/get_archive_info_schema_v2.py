import logging

from marshmallow import post_load
from marshmallow.fields import Bool, Int, String
from src.models.api.schema.refresh import BaseSchema

from src.models.v2.job.get_archive_info_job_v2 import GetArchiveInfoJobV2

logger = logging.getLogger(__name__)


class GetArchiveInfoSchemaV2(BaseSchema):
    """
    This validates the patron input in the get request
    """

    url = String(required=True)
    timeout = Int(required=False)

    # noinspection PyUnusedLocal
    @post_load
    # NB: **kwargs is needed here despite what the validator claims
    def post_load_function(self, data, **kwargs) -> GetUrlInfoJobV2:  # type: ignore # dead: disable
        """
        Returns GetArchiveInfoJobV2 result as job object
        """

        job = GetArchiveInfoJobV2(**data)
        job.validate_fields()

        return job
