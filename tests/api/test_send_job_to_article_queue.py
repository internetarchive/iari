from unittest import TestCase

from pydantic import ValidationError

from src.models.api.send_job_to_article_queue import SendJobToArticleQueue
from src.models.message import Message


class TestSendJobToArticleQueue(TestCase):
    def test_publish_job_missing_everything(self):
        with self.assertRaises(ValidationError):
            SendJobToArticleQueue()  # type: ignore # mypy: ignore

    def test_publish_job(self):
        queue = SendJobToArticleQueue(
            #language_code="en", wikimedia_site="wikipedia",
            message=Message(title="Test"), testing=True
        )
        assert queue.publish_to_article_queue() is True
