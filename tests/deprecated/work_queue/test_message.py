# from unittest import TestCase
#
# from src.models.message import Message
#
#
# class TestMessage(TestCase):
#     def test_process_data_no_cache(self):
#         m = Message()
#         with self.assertRaises(ValueError):
#             m.process_data()
#
#     def test_process_data_no_cache_testing(self):
#         m = Message()
#         m.process_data(testing=True)
#
#     def test_process_data_with_cache(self):
#         m = Message()
#         m.__setup_cache__()
#         m.process_data(testing=False)
