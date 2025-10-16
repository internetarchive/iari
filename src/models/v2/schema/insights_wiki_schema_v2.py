from marshmallow import fields, pre_load, post_load

from src.models.v2.job.insights_wiki_job_v2 import InsightsWikiJobV2
from src.models.v2.schema import BaseSchemaV2


class InsightsWikiSchemaV2(BaseSchemaV2):
    # Defines expected parameters for endpoint "insights"
    #   - default parameters are defined in BaseSchemaV2

    date_start = fields.Str(default=None, required=False)
    date_end = fields.Str(default=None, required=False)

    # noinspection PyUnusedLocal
    @post_load
    # NB: post_load is a marshmallow directive;
    #   this function is run after loading request args
    #   it basically pulls the request object value into a Job object
    #
    #  **kwargs is needed here despite what the validator claims
    def return_job_object(self, data, **kwargs) -> InsightsWikiJobV2:  # type: ignore # dead: disable
        """Return Job object"""
        from src import app
        app.logger.debug("==> InsightsWikiJobV2::@post_load:return_job_object")
        app.logger.debug(f"return_job_object data: {data}")

        job = InsightsWikiJobV2(**data)
        job.validate_fields()

        # NB here is where we can modify job field values before returning if we want

        return job
