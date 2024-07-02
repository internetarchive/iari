from marshmallow import fields, post_load

from src.models.v2.job.editref_job_v2 import EditRefJobV2
from src.models.v2.schema import BaseSchemaV2


class EditRefSchemaV2(BaseSchemaV2):
    # Defines expected parameters for EditRefV2 endpoint
    #   - default parameters are defined in BaseSchemaV2

    target = fields.Str(required=True)
    replace = fields.Str(required=True)
    source = fields.Str(required=True)

    # noinspection PyUnusedLocal
    @post_load
    # NB: post_load is a marshmallow directive; this function is run after loading request args
    #   **kwargs is needed here despite what the validator claims
    def return_job_object(self, data, **kwargs) -> EditRefJobV2:  # type: ignore # dead: disable
        """Return Job object"""
        from src import app
        app.logger.debug("==> EditRefSchemaV2::@post_load:return_job_object")

        job = EditRefJobV2(**data)
        job.validate_fields()

        # NB we can modify job field values here before returning

        return job
