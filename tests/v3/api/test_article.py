import json
from unittest import TestCase

from flask import Flask
from flask_restful import Api  # type: ignore

from src import Article
from src.v2.helpers.console import console
from src.v2.models.api.statistic.article import ArticleStatistics

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

    def test_valid_request_svwiki1(self):
        response = self.test_client.get(
            "/get-statistics?url=https://sv.wikipedia.org/wiki/Boy_Rozendal&testing=true&regex=test"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        console.print(data)
        assert data["title"] == "Boy_Rozendal"
        assert len(data["dehydrated_references"]) == 3
        assert len(data["urls"]) == 5

    def test_valid_request_dawiki1(self):
        response = self.test_client.get(
            "/get-statistics?url=https://da.wikipedia.org/wiki/Kleptoparasitisme&testing=true&regex=test"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        # console.print(data)
        assert data["title"] == "Kleptoparasitisme"
        assert len(data["dehydrated_references"]) == 35
        # print(len(data["urls"]))
        assert len(data["urls"]) == 21

    def test_valid_request_enwiki_test_refresh_true(self):
        response = self.test_client.get(
            "/get-statistics?url=https://en.wikipedia.org/wiki/Test&testing=True&refresh=True&regex=test"
        )
        data = json.loads(response.data)
        print(response.data)
        self.assertEqual(200, response.status_code)
        stats = ArticleStatistics(**data)
        assert stats.served_from_cache is False
