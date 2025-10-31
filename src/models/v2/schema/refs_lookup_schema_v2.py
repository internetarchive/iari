from marshmallow import fields, pre_load, post_load, validate

from src.models.v2.job.refs_lookup_job_v2 import RefsLookupJobV2
from src.models.v2.schema import BaseSchemaV2


class RefsLookupSchemaV2(BaseSchemaV2):
    # Defines endpoint parameters for refs_lookup
    #   - default parameters are defined in BaseSchemaV2

    url = fields.Str(required=True, validate=validate.Length(min=1))  # could add regex validation
    raw = fields.Bool(required=False)
    output= fields.String(required=False)


    @pre_load
    # NB: pre_load is a marshmallow directive;
    def process_input(self, data, **kwargs):
        """
        transform anything here that needs it
        """
        from src import app
        app.logger.debug(f"==> RefsLookupSchemaV2::(@pre_load)process_input: data:{data}")

        return data


    # noinspection PyUnusedLocal
    @post_load
    # NB: post_load is a marshmallow directive;
    #   this function is run after loading request args
    #   it basically pulls the request object data into a Job object
    #
    #  **kwargs is needed here despite what the validator claims
    def return_job_object(self, data, **kwargs) -> RefsLookupJobV2:  # type: ignore # dead: disable
        """Return Job object"""
        from src import app
        app.logger.debug("==> ExtractRefsJobV2::@post_load:return_job_object")
        app.logger.debug(f"return_job_object data: {data}")

        job = RefsLookupJobV2(**data)
        job.validate_fields()

        # NB here is where we can modify job field values before returning if we want

        return job
