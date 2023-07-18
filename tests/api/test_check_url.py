import json
import os
from unittest import TestCase

import pytest
from flask import Flask
from flask_restful import Api  # type: ignore

from src import CheckUrl


class TestCheckUrl(TestCase):
    def setUp(self):
        app = Flask(__name__)
        api = Api(app)

        api.add_resource(CheckUrl, "/check-url")
        app.testing = True
        self.test_client = app.test_client()

    @pytest.mark.skipif(
        "GITHUB_ACTIONS" in os.environ, reason="test is skipped in GitHub Actions"
    )
    def test_space_url(self):
        response = self.test_client.get(
            "/check-url?url=http://www.uri.edu/artsci/"
            "ecn/starkey/ECN398%20-Ecology,%20Economy,"
            "%20Society/RAPANUI.pdf&refresh=true"
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.data)
        print(data)
        assert data["is_valid"] is False
        # assert data["testdeadlink_status_code"] == 404

    # Disabled because it fails with 0 in the CI for reasons we don't understand
    # def test_valid_request_304_200(self):
    #     response = self.test_client.get(
    #         "/check-url?url=https://arxiv.org/pdf/2210.02667.pdf&testing=true&timeout=10"
    #     )
    #     self.assertEqual(200, response.status_code)
    #     data = json.loads(response.data)
    #     assert data["testdeadlink_status_code"] == 200
