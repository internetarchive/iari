# from unittest import TestCase
#
# from pydantic import ValidationError
#
# from src.models.message import Message
#
# from src.models.work_queue import WorkQueue
#
#
# class TestWorkQueue(TestCase):
#     def test_publish_with_wikibase(self):
#         w = WorkQueue(wikibase_deprecated=IASandboxWikibase())
#         w.__setup_cache__()
#         message = Message(wikibase_deprecated=IASandboxWikibase(), title="Test")
#         assert w.publish(message=message) is True
#
#     def test_publish_without_wikibase(self):
#         w = WorkQueue(wikibase_deprecated=IASandboxWikibase())
#         w.__setup_cache__()
#         message = Message(title="Test")
#         assert w.publish(message=message) is True
#
#     def test_publish_no_message(self):
#         w = WorkQueue(wikibase_deprecated=IASandboxWikibase())
#         w.__setup_cache__()
#         with self.assertRaises(ValidationError):
#             w.publish()  # type: ignore
#
#     def test_listen(self):
#         w = WorkQueue(wikibase_deprecated=IASandboxWikibase(), testing=True)
#         w.__setup_cache__()
#         w.listen_to_queue()
