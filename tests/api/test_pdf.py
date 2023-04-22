import json
from unittest import TestCase

from flask import Flask
from flask_restful import Api  # type: ignore

from src import Pdf
from src.helpers.console import console


class TestPdf(TestCase):
    def setUp(self):
        app = Flask(__name__)
        api = Api(app)

        api.add_resource(Pdf, "/statistics/pdf")
        app.testing = True
        self.test_client = app.test_client()

    def test_valid_request_test_pdf(self):
        response = self.test_client.get(
            "/statistics/pdf?url=https://s1.q4cdn.com/806093406/files/doc_downloads/test.pdf"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        console.print(data)
        exit()

    def test_valid_request_nonexistent_pdf(self):
        response = self.test_client.get(
            "/statistics/pdf?url=https://example.com/nonexistent.pdf"
        )
        self.assertEqual(400, response.status_code)
        data = json.loads(response.data)
        console.print(data)
        assert data["error"] == "Invalid URL: https://example.com/nonexistent.pdf"
