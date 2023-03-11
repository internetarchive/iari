import logging

from marshmallow import Schema, post_load
from marshmallow.fields import String, Int

from src.models.api.job.check_doi_job import CheckDoiJob

logger = logging.getLogger(__name__)


class CheckDoiSchema(Schema):
    """This validates the patron input in the get request"""

    doi = String()
    timeout = Int()
    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> CheckDoiJob:  # type: ignore # dead: disable
        """Return job object"""
        logger.debug("return_object: running")
        job = CheckDoiJob(**data)
        return job
