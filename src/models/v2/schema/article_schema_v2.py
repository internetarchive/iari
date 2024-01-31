import logging

from marshmallow import fields, post_load

from src.models.v2.job.article_job_v2 import ArticleJobV2
from src.models.v2.schema import BaseSchemaV2

logger = logging.getLogger(__name__)


class ArticleSchemaV2(BaseSchemaV2):
    # NB This defines the parameters expected for the endpoint that uses this class
    #   additional default parameters are defined in BaseSchemV2
    # WTF: are these marshmallow style declarations?
    url = fields.Str(required=True)
    reference_types = fields.Str(required=False)
    url_details = fields.Bool(required=False)
    url_method = fields.Str(required=False)

    # noinspection PyUnusedLocal
    @post_load
    # runs after request args are loaded
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> ArticleJobV2:  # type: ignore # dead: disable
        """Return job object"""
        from src import app

        app.logger.debug("ArticleSchemaV2::@post_load:return_object")

        job = ArticleJobV2(**data)
        job.validate_sections_and_extract_url()
        # NB it looks like this is checking the sections parameter (which is now defunct, i think?)
        #   and extracts the parts of the url from the url parameter
        return job
