import json
from unittest import TestCase

from src.models.work_queue import WorkQueue


class TestWorkQueue(TestCase):
    def test_publish_test(self):
        w = WorkQueue()
        w.publish(message=bytes(json.dumps(dict(test="test")), "utf-8"))

    def test_listen(self):
        w = WorkQueue()
        w.listen_to_queue()
