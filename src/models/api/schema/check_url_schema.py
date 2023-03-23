import logging

from marshmallow import post_load
from marshmallow.fields import Int, String

from src.models.api.job.check_url_job import CheckUrlJob
from src.models.api.schema import RefreshSchema

logger = logging.getLogger(__name__)


class CheckUrlSchema(RefreshSchema):
    """This validates the patron input in the get request"""

    url = String()
    timeout = Int()

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> CheckUrlJob:  # type: ignore # dead: disable
        """Return job object"""
        from src.models.api import app

        app.logger.debug("return_object: running")
        job = CheckUrlJob(**data)
        return job
