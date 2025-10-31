import logging

from marshmallow import fields, post_load

from src.models.v2.job.article_cache_job_v2 import ArticleCacheJobV2
from src.models.v2.schema import BaseSchemaV2

logger = logging.getLogger(__name__)


class ArticleCacheSchemaV2(BaseSchemaV2):
    # marshmallow style declarations
    iari_id = fields.Str(required=True)
    article_version = fields.Int(load_default=1)  # version 1 is original, 2 is V2

    # noinspection PyUnusedLocal
    @post_load
    # runs after request args are loaded
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> ArticleCacheJobV2:  # type: ignore # dead: disable
        """Return job object"""
        from src import app

        app.logger.debug("ArticleCacheSchemaV2::@post_load:return_object")

        job = ArticleCacheJobV2(**data)
        return job
