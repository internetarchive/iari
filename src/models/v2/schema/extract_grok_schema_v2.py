from marshmallow import fields, pre_load, post_load, validates_schema, ValidationError

from src.models.v2.job.extract_grok_job_v2 import ExtractGrokJobV2
from src.models.v2.schema import BaseSchemaV2

from flask import request

class ExtractGrokSchemaV2(BaseSchemaV2):

    page_title = fields.Str(required=True)
    # eventually we want to allow either pages or page_title to be required
    # # page_title = fields.Str(load_default="", required=False)
    # # pages = fields.List(fields.String(), required=False)
    use_local_cache = fields.Bool(load_default=False)

    # @pre_load
    # # NB: pre_load is a marshmallow directive;
    # def process_input(self, data, **kwargs):
    #     # """
    #     # transform comma separated pages into a List
    #     # """
    #     from src import app
    #     app.logger.debug(f"==> ExtractGrokSchemaV2::(@pre_load)process_input: data:{data}")
    #
    #     mutable_data = dict(data)  # Convert ImmutableMultiDict to a mutable dict
    #
    #     if 'pages' in mutable_data and isinstance(mutable_data['pages'], str):
    #         mutable_data['pages'] = mutable_data['pages'].split('|')
    #
    #     return mutable_data

    @validates_schema
    def validate_pages_or_title(self, data, **kwargs):
        # if not data.get("pages") and not data.get("page_title"):
        #     raise ValidationError("Either 'pages' or 'page_title' must be provided.")
        pass

    # noinspection PyUnusedLocal
    # NB: post_load is a marshmallow directive;
    #   this function is run after loading request args
    #   it basically pulls the request object data into a Job object
    #
    #  **kwargs is needed here despite what the validator claims
    @post_load
    def return_job_object(self, data, **kwargs) -> ExtractGrokJobV2:  # type: ignore # dead: disable
        """Return Job object"""
        from src import app
        app.logger.debug("==> ExtractGrokJobV2::@post_load:return_job_object")
        app.logger.debug(f"return_job_object data: {data}")

        app.logger.debug(
            f"request.args use_local_cache = "
            f"{request.args.get('use_local_cache')!r}"
        )
        app.logger.debug(
            f"***** use_local_cache: {data.get('use_local_cache')} "
            f"(type: {type(data.get('use_local_cache'))})"
        )
        app.logger.debug("Deserialized fields:")
        for k, v in data.items():
            app.logger.debug(f"  {k} = {v!r} ({type(v).__name__})")


        job = ExtractGrokJobV2(**data)
        job.validate_fields()

        # NB here is where we can modify job field values before returning if we want

        return job
