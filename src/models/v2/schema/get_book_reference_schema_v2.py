from marshmallow import fields, post_load

from src.models.v2.job.get_book_reference_job import GetBookReferenceJobV2
from src.models.v2.schema import BaseSchemaV2


class GetBookReferenceSchemaV2(BaseSchemaV2):
    # Defines expected parameters for GetBookReferenceV2 endpoint
    #   - default parameters are defined in BaseSchemaV2

    book_ref = fields.Str(required=True)
    # new_ref = fields.Str(required=True)
    # source = fields.Str(required=False)
    # wiki_page_url = fields.Str(required=False)

    # noinspection PyUnusedLocal
    @post_load
    # NB: post_load is a marshmallow directive that causes the following function to run after loading request args
    #   **kwargs is needed here despite what the validator claims
    def return_job_object(self, data, **kwargs) -> GetBookReferenceJobV2:  # type: ignore # dead: disable
        """Return Job object"""
        from src import app
        app.logger.debug("==> GetBookReferenceJobV2::@post_load:return_job_object")

        job = GetBookReferenceJobV2(**data)
        job.validate_fields()

        # NB we can modify job field values here before returning

        return job
