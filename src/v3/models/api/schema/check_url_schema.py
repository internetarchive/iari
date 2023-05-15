import logging

from marshmallow import post_load
from marshmallow.fields import Int, String

from src.v3.models.api.job.check_url_job import UrlJob
from src.v3.models.api.schema.refresh import BaseSchema

logger = logging.getLogger(__name__)


class UrlSchema(BaseSchema):
    """This validates the patron input in the get request"""

    url = String()
    timeout = Int()

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> UrlJob:  # type: ignore # dead: disable
        """Return job object"""
        from src import app

        app.logger.debug("return_object: running")
        job = UrlJob(**data)
        return job
