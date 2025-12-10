from marshmallow import fields, pre_load, post_load

from src.models.v2.job.wiki_signals_job_v2 import WikiSignalsJobV2
from src.models.v2.schema import BaseSchemaV2


class WikiSignalsSchemaV2(BaseSchemaV2):
    # Defines expected parameters for endpoint "wiki_signals"
    #   - default parameters are defined in BaseSchemaV2

    domain = fields.Str(required=True)

    # noinspection PyUnusedLocal
    @post_load
    # NB: post_load is a marshmallow directive that directs this function
    #   to run after loading request args. It basically moves the request
    #   object values into a Job object
    #
    #  **kwargs is needed here despite what the validator claims
    def return_job_object(self, data, **kwargs) -> WikiSignalsJobV2:  # type: ignore # dead: disable
        """Return Job object"""
        job = WikiSignalsJobV2(**data)
        job.validate_fields()

        # NB here is where we can modify job field values before returning if we want

        # NB TODO is this where we replace domai name with extracted domain if domain is a url?

        return job
