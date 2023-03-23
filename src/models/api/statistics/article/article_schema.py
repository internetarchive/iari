import logging

from marshmallow import Schema, fields, post_load

from src import WikimediaDomain
from src.models.api.enums import Lang
from src.models.api.job.article_job import ArticleJob

logger = logging.getLogger(__name__)


class ArticleSchema(Schema):
    lang = fields.Enum(enum=Lang, required=False)
    refresh = fields.Bool(required=False)
    site = fields.Enum(enum=WikimediaDomain, required=False)
    testing = fields.Bool(required=False)
    title = fields.Str(required=False)
    url = fields.Str(required=False)

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> ArticleJob:  # type: ignore # dead: disable
        """Return job object"""
        from src.models.api import app

        app.logger.debug("return_object: running")
        job = ArticleJob(**data)
        job.extract_url()
        job.urldecode_title()
        # print(job.title)
        return job
