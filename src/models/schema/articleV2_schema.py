import logging

from marshmallow import fields, post_load

from src.models.api.job.article_job import ArticleV2Job
from src.models.api.schema.refresh import BaseSchema

logger = logging.getLogger(__name__)


class ArticleV2Schema(BaseSchema):
    url = fields.Str(required=True)
    reference_types = fields.Str(required=False)
    url_details = fields.Bool(required=False)
    url_method = fields.Str(required=False)

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> ArticleJob:  # type: ignore # dead: disable
        """Return job object"""
        from src import app

        app.logger.debug("ArticleV2Schema: running")

        job = ArticleV2Job(**data)
        job.validate_sections_and_extract_url()
        return job
