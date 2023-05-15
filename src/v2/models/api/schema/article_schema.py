import logging

from marshmallow import fields, post_load

from src.v2.models.api.job.article_job import ArticleJob
from src.v2.models.api.schema.refresh import BaseSchema

logger = logging.getLogger(__name__)


class ArticleSchema(BaseSchema):
    url = fields.Str(required=True)
    regex = fields.Str(required=True)

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> ArticleJob:  # type: ignore # dead: disable
        """Return job object"""
        from src import app

        app.logger.debug("return_object: running")
        job = ArticleJob(**data)
        job.validate_regex_and_extract_url()
        return job
