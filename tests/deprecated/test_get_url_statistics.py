# import json
# import logging
# from unittest import TestCase
#
# from flask import Flask
# from flask_restful import Api  # type: ignore
#
# from src.helpers.console import console
#
# logger = logging.getLogger(__name__)
#
# # This is needed to get the full diff when tests fail
# # https://stackoverflow.com/questions/14493670/how-to-set-self-maxdiff-in-nose-to-get-full-diff-output
# # TestCase.maxDiff = None
#
#
# class TestGetUrlStatistics(TestCase):
#     def setUp(self):
#         app = Flask(__name__)
#         api = Api(app)
#
#         api.add_resource(GetUrlStatistics, "/get-urls")
#         app.testing = True
#         self.test_client = app.test_client()
#
#     # DISABLED because it fails
#     # def test_valid_request_electrical_breakdown(self):
#     #     response = self.test_client.get(
#     #         "/get-statistics?lang=en&site=wikipedia&title=Electrical_breakdown&testing=True"
#     #     )
#     #     data = json.loads(response.data)
#     #     print(response.data)
#     #     self.assertEqual(200, response.status_code)
#     #     self.assertEqual(
#     #         ArticleStatistics(title="Electrical_breakdown").dict(),
#     #         ArticleStatistics(**self.__make_reproducible__(data=data)).dict(),
#     #     )
#
#     # DISABLED because it takes forever
#     # def test_valid_request_gnu_linux_naming_controversy(self):
#     #     response = self.test_client.get(
#     #         "get-statistics?lang=en&site=wikipedia&title=GNU/Linux_naming_controversy"
#     #     )
#     #     logger.debug(response.data)
#     #     # data = json.loads(response.data)
#     #     self.assertEqual(200, response.status_code)
#
#     def test_valid_request_easter_island(self):
#         """This tests against an excerpt of the whole article (head+tail)"""
#         # print(self.test_client)
#         # exit()
#         response = self.test_client.get(
#             "/get-urls?lang=en&site=wikipedia&title=Easter Island&testing=True"
#         )
#         data = json.loads(response.data)
#         console.print(data)
#         # exit()
#         self.assertEqual(200, response.status_code)
#         stat = UrlStatistics(**self.__make_reproducible__(data=data))
#         assert stat.urls is not None
#         urls = stat.urls
#         assert urls.urls_found is True
#         assert stat.title == "Easter Island"
#         assert stat.site == "wikipedia"
#         assert stat.page_id == 0
#         assert stat.timing == 0
#         assert stat.timestamp == 0
#         url_details = stat.url_details
#         # This is empty because we don't check the urls during testing
#         assert len(url_details) == 0
#         agg = urls.agg
#         assert isinstance(agg, UrlsAggregates)
#         uagg = agg
#         assert uagg.all == 5
#         uuagg = agg.unique
#         # We dont check urls during this
#         # test for speed reasons so all these are 0
#         assert uuagg.all == 0
#         assert uuagg.error == 0
#         assert uuagg.s5xx == 0
#         assert uuagg.s404 == 0
#         assert uuagg.s200 == 0
#         assert uuagg.s3xx == 0
#         assert uuagg.malformed_urls == 0
#         assert uuagg.no_dns == 0
#         assert uuagg.other_2xx == 0
#         assert uuagg.other_4xx == 0
#
#     def test_invalid_language(self):
#         response = self.test_client.get("/get-urls?lang=fr&site=wikipedia&title=Test")
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(
#             b"{\"error\": \"{'lang': ['Must be one of: en.']}\"}\n", response.data
#         )  # expected output
#
#     def test_missing_title(self):
#         response = self.test_client.get("/get-urls?lang=en&site=wikipedia")
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(
#             response.data,
#             b"{\"error\": \"{'title': ['Missing data for required field.']}\"}\n",
#         )
#
#     def test_invalid_site(self):
#         response = self.test_client.get("/get-urls?lang=en&site=example.com&title=Test")
#         print(response.data)
#         self.assertEqual(400, response.status_code)
#         self.assertEqual(
#             b"{\"error\": \"{'site': ['Must be one of: wikipedia.']}\"}\n",
#             response.data,
#         )
#
#     def test_site_capitalized(self):
#         response = self.test_client.get("/get-urls?lang=en&site=WIKIPEDIA&title=Test")
#         # print(response.data)
#         self.assertEqual(400, response.status_code)
#
#     def test_valid_site(self):
#         response = self.test_client.get("/get-urls?lang=en&site=wikipedia&title=Test")
#         # print(response.data)
#         self.assertEqual(200, response.status_code)
#
#     @staticmethod
#     def __make_reproducible__(data):
#         """Remove all timing information"""
#         # delete non reproducible output
#         data["timing"] = 0
#         data["timestamp"] = 0
#         return data
#
#     def test_valid_request_test_refresh_true(self):
#         response = self.test_client.get(
#             "/get-urls?lang=en&site=wikipedia&title=Test&testing=True&refresh=True"
#         )
#         data = json.loads(response.data)
#         print(response.data)
#         self.assertEqual(200, response.status_code)
#         stats = UrlStatistics(**data)
#         assert stats.served_from_cache is False
#         assert stats.refreshed_now is True
#
#     # def test_valid_request_test_refresh_false(self):
#     #     response = self.test_client.get(
#     #         "/get-urls?lang=en&site=wikipedia&title=Test&testing=True&refresh=False"
#     #     )
#     #     data = json.loads(response.data)
#     #     print(response.data)
#     #     self.assertEqual(200, response.status_code)
#     #     stats = UrlStatistics(**data)
#     #     assert stats.served_from_cache is True
#     #     assert stats.refreshed_now is False
#
#     def test___validate_and_get_job__(self):
#         """We dont test this since the dev/team does not yet
#         know how to mock flask that well yet.
#         We do however test the scheme in another file
#         and the job it returns"""
#         pass
#
#     def test_valid_request_sncaso_malformed(self):
#         response = self.test_client.get(
#             "/get-urls?lang=en&site=wikipedia&title=SNCASO&refresh=True&subset=malformed"
#         )
#         data = json.loads(response.data)
#         print(response.data)
#         self.assertEqual(200, response.status_code)
#         stats = UrlStatistics(**data)
#         assert len(stats.url_details) == 0
#         assert stats.served_from_cache is False
#         assert stats.refreshed_now is True
#
#     def test_valid_request_sncaso_not_found(self):
#         response = self.test_client.get(
#             "/get-urls?lang=en&site=wikipedia&title=SNCASO&refresh=True&subset=not_found"
#         )
#         data = json.loads(response.data)
#         print(response.data)
#         self.assertEqual(200, response.status_code)
#         stats = UrlStatistics(**data)
#         assert len(stats.url_details) == 0
#         assert stats.served_from_cache is False
#         assert stats.refreshed_now is True
