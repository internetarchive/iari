import logging

from marshmallow import post_load
from marshmallow.fields import Bool, Int, String

from src.models.api.job.check_urls_job import UrlsJob
from src.models.api.schema.refresh import BaseSchema

logger = logging.getLogger(__name__)


class UrlsSchema(BaseSchema):
    """This validates the patron input in the get request"""

    # curl "http://localhost:5000/v2/check-urls?url=https://www.nytimes.com/2009/01/21/opinion/21wed1.html&url=https://www.realclearpolitics.com/video/2009/02/moran_obama.html'

    url = String(required=True)  # multiple allowed
    timeout = Int(required=False)
    debug = Bool(required=False)
    blocks = Bool(required=False)
    xml = Bool(required=False)
    html = Bool(required=False)
    json_ = Bool(required=False)

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs) -> UrlsJob:  # type: ignore # dead: disable
        """Return job object"""
        from src import app

        app.logger.debug("return_object: running")

        job = UrlsJob(**data)
        return job
