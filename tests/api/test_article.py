import json
from unittest import TestCase

from flask import Flask
from flask_restful import Api  # type: ignore

from src import Article
from src.helpers.console import console
from src.models.api.statistic.article import ArticleStatistics

# This is needed to get the full diff when tests fail
# https://stackoverflow.com/questions/14493670/how-to-set-self-maxdiff-in-nose-to-get-full-diff-output
# TestCase.maxDiff = None


class TestArticle(TestCase):
    def setUp(self):
        app = Flask(__name__)
        api = Api(app)

        api.add_resource(Article, "/get-statistics")
        app.testing = True
        self.test_client = app.test_client()

    # Disabled because it fails in cli invocation of pytests
    # def test_valid_request_enwiki_easter_island(self):
    #     response = self.test_client.get(
    #         "/get-statistics?url=https://en.wikipedia.org/wiki/Easter_Island&testing=true&regex=test"
    #     )
    #     self.assertEqual(200, response.status_code)
    #     data = json.loads(response.data)
    #     console.print(data)
    #     assert data["title"] == "Easter_Island"
    #     assert len(data["dehydrated_references"]) > 1
    #     assert len(data["urls"]) > 1

    # todo use a specific revision instead when we support it
    def test_valid_request_svwiki1(self):
        response = self.test_client.get(
            "/get-statistics?url=https://sv.wikipedia.org/wiki/Boy_Rozendal&testing=true&regex=Externa%20länkar&refresh=true"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        # # will this test the cache? no because we dont cache during testing
        # del data["isodate"]
        # del data["timestamp"]
        # response2 = self.test_client.get(
        #     "/get-statistics?url=https://sv.wikipedia.org/wiki/Boy_Rozendal&testing=true&regex=Externa%20länkar&refresh=false"
        # )
        # self.assertEqual(200, response2.status_code)
        # data2 = json.loads(response2.data)
        # if "isodate" in data:
        #     del data["isodate"]
        # if "timestamp" in data:
        #     del data["timestamp"]
        # assert data == data2
        # console.print(data)
        assert data["title"] == "Boy_Rozendal"
        assert len(data["dehydrated_references"]) == 4
        # print(data["urls"])
        assert len(data["urls"]) == 4
        # fixme this fails because of https://github.com/internetarchive/iari/issues/836
        # assert len(data["fld_counts"]) == 4

    # todo use a specific revision instead when we support it
    # def test_valid_request_dawiki1(self):
    #     response = self.test_client.get(
    #         "/get-statistics?url=https://da.wikipedia.org/wiki/Kleptoparasitisme&testing=true&regex=test"
    #     )
    #     self.assertEqual(200, response.status_code)
    #     data = json.loads(response.data)
    #     # console.print(data)
    #     assert data["title"] == "Kleptoparasitisme"
    #     # print(len(data["dehydrated_references"]))
    #     # assert len(data["dehydrated_references"]) == 40
    #     # print(len(data["urls"]))
    #     assert len(data["urls"]) == 23
    #     # print(len(data["fld_counts"]))
    #     assert len(data["fld_counts"]) == 11
    #     assert data["fld_counts"] == {
    #         "africaninvertebrates.org": 1,
    #         "africaninvertebrates.org.za": 1,
    #         "americanarachnology.org": 1,
    #         "archive.org": 5,
    #         "bbc.co.uk": 1,
    #         "fcla.edu": 1,
    #         "google.com": 1,
    #         "nature.com": 1,
    #         "nina.no": 1,
    #         "oup.com": 1,
    #         "theguardian.com": 1,
    #         "unm.edu": 1,
    #     }

    def test_valid_request_enwiki_test_refresh_true(self):
        response = self.test_client.get(
            "/get-statistics?url=https://en.wikipedia.org/wiki/Test&testing=True&refresh=True&regex=test"
        )
        data = json.loads(response.data)
        print(response.data)
        self.assertEqual(200, response.status_code)
        stats = ArticleStatistics(**data)
        assert stats.served_from_cache is False
