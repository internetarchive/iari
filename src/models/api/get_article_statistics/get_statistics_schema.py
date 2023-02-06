import logging

from marshmallow import Schema, fields, post_load

from src import WikimediaSite
from src.models.api.job import Job

logger = logging.getLogger(__name__)


class GetStatisticsSchema(Schema):
    lang = fields.Str(required=True)
    refresh = fields.Bool(required=False)
    site = fields.Enum(enum=WikimediaSite, required=True)
    testing = fields.Bool(required=False)
    title = fields.Str(required=True)

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs):  # type: ignore # dead: disable
        """Return job object"""
        logger.debug("return_object: running")
        job = Job(**data)
        job.urldecode_title()
        # print(job.title)
        return job
