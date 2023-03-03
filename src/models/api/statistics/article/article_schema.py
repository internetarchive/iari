import logging

from marshmallow import Schema, fields, post_load

from src import WikimediaSite
from src.models.api.enums import Lang
from src.models.api.job.article_job import ArticleJob

logger = logging.getLogger(__name__)


class ArticleSchema(Schema):
    lang = fields.Enum(enum=Lang, required=True)
    refresh = fields.Bool(required=False)
    site = fields.Enum(enum=WikimediaSite, required=True)
    testing = fields.Bool(required=False)
    title = fields.Str(required=True)

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> ArticleJob:  # type: ignore # dead: disable
        """Return job object"""
        logger.debug("return_object: running")
        job = ArticleJob(**data)
        job.urldecode_title()
        # print(job.title)
        return job
