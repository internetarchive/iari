# import logging
# from unittest import TestCase
#
# from requests import HTTPError
#
# import config
# from src import WikiCitationsWikibase
# from src.models.wikibase.crud.read import WikibaseCrudRead
#
#
# logging.basicConfig(level=config.loglevel)
# logger = logging.getLogger(__name__)
#
#
# class TestWikibaseCrudRead(TestCase):
#     def test_get_items_via_sparql(self):
#         wc = WikibaseCrudRead(wikibase=IASandboxWikibase())
#         with self.assertRaises(HTTPError):
#             wc.__get_items_via_sparql__(query="test")
#
#     def test_get_all_items_and_hashes_sandbox(self):
#         wc = WikibaseCrudRead(wikibase=IASandboxWikibase())
#         result = wc.__get_all_items_and_hashes__()
#         count = 0
#         for entry in result:
#             count += 1
#             print(entry)
#             if count >= 10:
#                 break
#         assert count == 10
#
#     def test_get_all_items_and_hashes_wcd(self):
#         wc = WikibaseCrudRead(wikibase=WikiCitationsWikibase())
#         result = wc.__get_all_items_and_hashes__()
#         count = 0
#         for entry in result:
#             count += 1
#             print(entry)
#             if count >= 10:
#                 break
#         assert count == 10
