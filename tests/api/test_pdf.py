import json
from unittest import TestCase

from flask import Flask
from flask_restful import Api  # type: ignore

from src import Pdf


class TestPdf(TestCase):
    def setUp(self):
        app = Flask(__name__)
        api = Api(app)

        api.add_resource(Pdf, "/pdf")
        app.testing = True
        self.test_client = app.test_client()

    def test_valid_request_responsible_ai_no_debug(self):
        response = self.test_client.get(
            "/pdf?url=https://arxiv.org/pdf/2210.02667.pdf&testing=true&refresh=true"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        debug_keys = [
            "debug_text_original",
            "debug_text_without_linebreaks",
            "debug_text_without_spaces",
            "debug_url_annotations",
            "debug_html",
            "debug_xml",
            "debug_json",
            "debug_blocks",
        ]
        for key in debug_keys:
            assert key not in data

    def test_valid_request_responsible_ai_default_debug(self):
        response = self.test_client.get(
            "/pdf?url=https://arxiv.org/pdf/2210.02667.pdf&testing=true&refresh=true&debug=true"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        debug_keys = [
            "debug_html",
            "debug_xml",
            "debug_json",
            "debug_blocks",
        ]
        for key in debug_keys:
            assert key not in data

    def test_valid_request_responsible_ai_html_debug(self):
        response = self.test_client.get(
            "/pdf?url=https://arxiv.org/pdf/2210.02667.pdf&testing=true&refresh=true&debug=true&html=true"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        debug_keys = [
            "debug_xml",
            "debug_json",
            "debug_blocks",
        ]
        for key in debug_keys:
            assert key not in data

    def test_valid_request_responsible_ai_xml_debug(self):
        response = self.test_client.get(
            "/pdf?url=https://arxiv.org/pdf/2210.02667.pdf&testing=true&refresh=true&debug=true&xml=true"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        debug_keys = [
            "debug_html",
            "debug_json",
            "debug_blocks",
        ]
        for key in debug_keys:
            assert key not in data

    def test_valid_request_responsible_ai_json_debug(self):
        response = self.test_client.get(
            "/pdf?url=https://arxiv.org/pdf/2210.02667.pdf&testing=true&refresh=true&debug=true&json_=true"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        debug_keys = [
            "debug_html",
            "debug_xml",
            "debug_blocks",
        ]
        for key in debug_keys:
            assert key not in data

    def test_valid_request_responsible_ai_blocks_debug(self):
        response = self.test_client.get(
            "/pdf?url=https://arxiv.org/pdf/2210.02667.pdf&testing=true&refresh=true&debug=true&blocks=true"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        debug_keys = [
            "debug_html",
            "debug_xml",
            "debug_json",
        ]
        for key in debug_keys:
            assert key not in data
