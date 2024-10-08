from marshmallow import fields, pre_load, post_load

from src.models.v2.job.extract_refs_job_v2 import ExtractRefsJobV2
from src.models.v2.schema import BaseSchemaV2


class ExtractRefsSchemaV2(BaseSchemaV2):
    # Defines expected parameters for endpoint
    #   - default parameters are defined in BaseSchemaV2

    # which_wiki = fields.Str(default="enwiki")
    # pages = fields.List(fields.String(), required=False)  # either pages or wikitext must be defined
    # wikitext = fields.Str(required=False)  # if provided, overrides pages array

    page_title = fields.Str(default="", required=False)
    domain = fields.Str(default="en.wikipedia.org", required=False)
    as_of = fields.Str(default=None, required=False)
    wikitext = fields.Str(default="", required=False)

    @pre_load
    # NB: pre_load is a marshmallow directive;
    def process_input(self, data, **kwargs):
        """
        transform comma separated pages into a List
        """
        from src import app
        app.logger.debug(f"==> FetchRefsSchemaV2::(@pre_load)process_input: data:{data}")

        request_method = self.context.get('request_method', None)
        # if request_method:
        #     print(f"Request method received: {request_method}")

        app.logger.debug(f"==> ExtractRefsSchemaV2::(@pre_load)process_input: request_method:{request_method}")


        mutable_data = dict(data)  # Convert ImmutableMultiDict to a mutable dict
        if 'pages' in mutable_data and isinstance(mutable_data['pages'], str):
            mutable_data['pages'] = mutable_data['pages'].split('|')
        return mutable_data

    # noinspection PyUnusedLocal
    @post_load
    # NB: post_load is a marshmallow directive;
    #   this function is run after loading request args
    #   it basically pulls the request object value into a Job object
    #
    #  **kwargs is needed here despite what the validator claims
    def return_job_object(self, data, **kwargs) -> ExtractRefsJobV2:  # type: ignore # dead: disable
        """Return Job object"""
        from src import app
        app.logger.debug("==> ExtractRefsJobV2::@post_load:return_job_object")
        app.logger.debug(f"return_job_object data: {data}")

        job = ExtractRefsJobV2(**data)
        job.validate_fields()

        # NB here is where we can modify job field values before returning if we want

        return job
