import json
import logging

from pydantic import BaseModel

from src.models.work_queue import WorkQueue

logger = logging.getLogger(__name__)


class SendJobToArticleQueue(BaseModel):
    language_code: str
    wikimedia_site: str
    title: str
    testing: bool = False

    def publish_to_article_queue(self) -> bool:
        logger.debug("publish_to_article_queue: Running")
        data = dict(
            title=self.title,
            language_code=self.language_code,
            wikimedia_site=self.wikimedia_site,
        )

        logger.info(f"Publishing message with {data}")
        if not self.testing:
            work_queue = WorkQueue()
            return work_queue.publish(
                message=bytes(
                    json.dumps(data),
                    "utf-8",
                )
            )
        else:
            return False