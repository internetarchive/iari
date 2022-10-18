from typing import Optional

from flask import request # type: ignore
from flask_restful import Resource, abort # type: ignore

from app import logger
from src.helpers.console import console
from src.models.api.add_job_schema import AddJobSchema
from src.models.api.job import Job
from src.models.api.send_job_to_article_queue import SendJobToArticleQueue


class AddJobToQueue(Resource):
    schema = AddJobSchema()
    job: Optional[Job]

    def get(self):
        self.__validate_and_get_job__()
        # TODO handle URL encoding of the title
        if self.job.lang == "en" and self.job.title and self.job.site == "wikipedia":
            queue = SendJobToArticleQueue(
                language_code=self.job.lang,
                title=self.job.title,
                wikimedia_site=self.job.site,
            )
            logger.info("Publishing to queue")
            if self.job.testing:
                return "ok", 200
            else:
                queued = queue.publish_to_article_queue()
                if queued:
                    return "job queued", 201
                else:
                    return "server error, the job could not be queued", 500
        else:
            # Something was not valid, return a meaningful error
            logger.error("did not get what we need")
            if self.job.lang != "en":
                return "Only en language code is supported", 400
            if self.job.title == "":
                return "Title was missing", 400
            if self.job.site != "wikipedia":
                return "Only 'wikipedia' site is supported", 400

    def __validate_and_get_job__(self):
        self.__validate__()
        self.__parse_into_job__()

    def __validate__(self):
        errors = self.schema.validate(request.args)
        if errors:
            abort(400, error=str(errors))

    def __parse_into_job__(self):
        console.print(request.args)
        self.job = self.schema.load(request.args)
        console.print(self.job.dict())
