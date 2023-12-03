import logging

from marshmallow import post_load
from marshmallow.fields import Bool, Int, String

from src.models.api.job.check_url_archive_job import UrlArchiveJob
from src.models.api.schema.refresh import BaseSchema

logger = logging.getLogger(__name__)


class UrlArchiveSchema(BaseSchema):
    """This validates the patron input in the get request"""

    url = String(required=True)

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> UrlArchiveJob:  # type: ignore # dead: disable
        """Return job object"""
        from src import app

        app.logger.debug("return_object: running")
        job = UrlArchiveJob(**data)
        return job
