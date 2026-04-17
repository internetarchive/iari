from marshmallow import fields, pre_load, post_load

from src.models.v2.job.signals_docs_job_v2 import SignalsDocsJobV2
from src.models.v2.schema import BaseSchemaV2


class SignalsDocsSchemaV2(BaseSchemaV2):
    # Returns official documentation of WkiSignals
    #
    # no parameters

    # NB: post_load is a marshmallow directive that directs this function
    #   to run after loading request args.
    #
    #   It basically moves request object values into Job object, which is returned
    #
    #  **kwargs is needed here despite what the validator claims
    @post_load
    def return_job_object(self, data, **kwargs) -> SignalsDocsJobV2:  # type: ignore # dead: disable
        """
        return Job object
        """

        job = SignalsDocsJobV2(**data)
        job.validate_fields()

        return job
