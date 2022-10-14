import json
from unittest import TestCase

from src.models.message import Message
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.work_queue import WorkQueue


class TestWorkQueue(TestCase):
    def test_publish_test(self):
        w = WorkQueue()
        message = Message(wikibase=IASandboxWikibase(), title="Test")
        w.publish(message=message)

    def test_listen(self):
        w = WorkQueue()
        w.listen_to_queue()
