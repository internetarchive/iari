import logging

from marshmallow import fields, post_load

from src.models.api.job.article_job import ArticleJob
from src.models.api.schema import RefreshSchema

logger = logging.getLogger(__name__)


class ArticleSchema(RefreshSchema):
    testing = fields.Bool(required=False)
    url = fields.Str(required=True)

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> ArticleJob:  # type: ignore # dead: disable
        """Return job object"""
        from src.models.api import app

        app.logger.debug("return_object: running")
        job = ArticleJob(**data)
        job.extract_url()
        # print(job.title)
        return job
