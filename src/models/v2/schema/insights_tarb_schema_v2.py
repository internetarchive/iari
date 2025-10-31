from marshmallow import fields, pre_load, post_load

from src.models.v2.job.insights_tarb_job_v2 import InsightsTarbJobV2
from src.models.v2.schema import BaseSchemaV2


class InsightsTarbSchemaV2(BaseSchemaV2):
    # Defines expected parameters for endpoint "insights"
    #   - default parameters are defined in BaseSchemaV2

    date_start = fields.Str(required=False, allow_none=True, load_default=None)
    date_end = fields.Str(required=False, allow_none=True, load_default=None)

    # noinspection PyUnusedLocal
    @post_load
    # NB: post_load is a marshmallow directive;
    #   this function is run after loading request args
    #   it basically pulls the request object value into a Job object
    #
    #  **kwargs is needed here despite what the validator claims
    def return_job_object(self, data, **kwargs) -> InsightsTarbJobV2:  # type: ignore # dead: disable
        """Return Job object"""
        job = InsightsTarbJobV2(**data)
        job.validate_fields()

        # NB here is where we can modify job field values before returning if we want

        return job
