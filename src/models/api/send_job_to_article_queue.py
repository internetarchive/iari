import logging

from pydantic import BaseModel

import config
from src.models.message import Message
from src.models.work_queue import WorkQueue

logger = logging.getLogger(__name__)


class SendJobToArticleQueue(BaseModel):
    message: Message
    testing: bool = False

    def publish_to_article_queue(self) -> bool:
        logger.debug("publish_to_article_queue: Running")
        logger.info(f"Publishing message with {self.message.dict()}")
        if not self.testing:
            work_queue = WorkQueue(wikibase=config.wikicitations_api_wikibase_backend)
            return work_queue.publish(message=self.message)
        else:
            return False
