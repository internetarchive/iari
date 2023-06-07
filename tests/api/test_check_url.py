import json
from unittest import TestCase

from flask import Flask
from flask_restful import Api  # type: ignore

from src import CheckUrl, Pdf


class TestPdf(TestCase):
    def setUp(self):
        app = Flask(__name__)
        api = Api(app)

        api.add_resource(CheckUrl, "/check-url")
        app.testing = True
        self.test_client = app.test_client()

    def test_valid_request_304_200(self):
        response = self.test_client.get(
            "/check-url?url=https://arxiv.org/pdf/2210.02667.pdf&testing=true"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        assert data["testdeadlink_status_code"] == 200
        assert data["status_code"] == 304
