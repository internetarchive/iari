from marshmallow import Schema, post_load
from marshmallow.fields import Int, String

from src.models.api.job.check_doi_job import CheckDoiJob


class CheckDoiSchema(Schema):
    """This validates the patron input in the get request"""

    doi = String()
    timeout = Int()

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> CheckDoiJob:  # type: ignore # dead: disable
        """Return job object"""
        from src.models.api import app

        app.logger.debug("return_object: running")
        job = CheckDoiJob(**data)
        return job
