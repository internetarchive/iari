import json
from unittest import TestCase

from pydantic import ValidationError

from src.models.work_queue import WorkQueue


class TestWorkQueue(TestCase):
    def test_publish_with_message(self):
        w = WorkQueue()
        assert w.publish(message=bytes(json.dumps(dict(test="test")), "utf-8")) is True

    def test_listen(self):
        w = WorkQueue()
        w.listen_to_queue()

    def test_publish_no_message(self):
        wq = WorkQueue()
        with self.assertRaises(ValidationError):
            assert wq.publish() is True
