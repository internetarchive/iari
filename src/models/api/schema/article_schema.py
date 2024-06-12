import logging

from marshmallow import fields, post_load

from src.models.api.job.article_job import ArticleJob
from src.models.api.schema.refresh import BaseSchema

logger = logging.getLogger(__name__)


class ArticleSchema(BaseSchema):
    url = fields.Str(required=True)
    revision = fields.Int(required=False)
    # regex = fields.Str(required=True)
    sections = fields.Str(required=False)
    dehydrate = fields.Bool(required=False)

    # noinspection PyUnusedLocal
    @post_load
    # NB: post_load is a marshmallow directive that runs the function after loading
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> ArticleJob:  # type: ignore # dead: disable
        """Return job object"""
        from src import app

        app.logger.debug("return_object: running")
        job = ArticleJob(**data)
        job.validate_sections_and_extract_url()
        return job
