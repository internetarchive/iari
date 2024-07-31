from marshmallow import fields, pre_load, post_load

from src.models.v2.job.fetchrefs_job_v2 import FetchRefsJobV2
from src.models.v2.schema import BaseSchemaV2


class FetchRefsSchemaV2(BaseSchemaV2):
    # Defines expected parameters for endpoint
    #   - default parameters are defined in BaseSchemaV2

    which_wiki = fields.Str(default="enwiki")
    pages = fields.List(fields.String(), required=False)  # either pages or wikitext must be defined
    wikitext = fields.Str(required=False)  # if provided, overrides pages array

    @pre_load
    def process_input(self, data, **kwargs):
        """
        transform comma separated pages into a List
        """
        mutable_data = dict(data)  # Convert ImmutableMultiDict to a mutable dict
        if 'pages' in mutable_data and isinstance(mutable_data['pages'], str):
            mutable_data['pages'] = mutable_data['pages'].split(',')
        return mutable_data

    # noinspection PyUnusedLocal
    @post_load
    # NB: post_load is a marshmallow directive;
    #   this function is run after loading request args
    #   it basically pulls the values from the request object into a Job object
    #
    #  **kwargs is needed here despite what the validator claims
    def return_job_object(self, data, **kwargs) -> FetchRefsJobV2:  # type: ignore # dead: disable
        """Return Job object"""
        from src import app
        app.logger.debug("==> FetchRefsSchemaV2::@post_load:return_job_object")

        app.logger.debug(f"return_job_object data: {data}")

        # app.logger.debug(f"return_job_object **data: {**data}")


        job = FetchRefsJobV2(**data)
        job.validate_fields()

        # NB here is where we can modify job field values before returning if we want

        return job
