from marshmallow import fields, pre_load, post_load

from src.models.v2.job.signals_job_v2 import SignalsJobV2
from src.models.v2.schema import BaseSchemaV2


class SignalsSchemaV2(BaseSchemaV2):
    # Defines expected parameters for endpoint "wiki_signals"
    #   - default parameters are defined in BaseSchemaV2

    domain = fields.Str(required=False)
    url = fields.Str(required=False)

    # noinspection PyUnusedLocal

    # NB: post_load is a marshmallow directive that directs this function
    #   to run after loading request args.
    #
    #   It basically moves request object values into Job object, which is returned
    #
    #  **kwargs is needed here despite what the validator claims
    @post_load
    def return_job_object(self, data, **kwargs) -> SignalsJobV2:  # type: ignore # dead: disable
        """
        return Job object
        """

        job = SignalsJobV2(**data)
        job.validate_fields()

        # NB: mved these issue to SignalsJobV2
        # NB here is where we can modify job field values before returning if we want
        # NB TODO is this where we replace domain name with extracted domain if domain is a url?

        return job
