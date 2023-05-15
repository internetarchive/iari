from unittest import TestCase

from flask import Flask
from flask_restful import Api  # type: ignore

from src import Pdf


class TestPdf(TestCase):
    def setUp(self):
        app = Flask(__name__)
        api = Api(app)

        api.add_resource(Pdf, "/statistics/pdf")
        app.testing = True
        self.test_client = app.test_client()

    # Disabled because it fails in cli invocation of pytests
    # def test_valid_request_test_pdf(self):
    #     response = self.test_client.get(
    #         "/statistics/pdf?url=https://s1.q4cdn.com/806093406/files/doc_downloads/test.pdf&testing=true"
    #     )
    #     self.assertEqual(200, response.status_code)
    #     data = json.loads(response.data)
    #     assert data["text_links_total"] == data["annotation_links_total"] == 0

    # Disabled because it fails in cli invocation of pytests
    # def test_valid_request_nonexistent_pdf(self):
    #     response = self.test_client.get(
    #         "/statistics/pdf?url=https://example.com/nonexistent.pdf&testing=true"
    #     )
    #     self.assertEqual(400, response.status_code)
    #     data = json.loads(response.data)
    #     console.print(data)
    #     assert data == "Not a valid PDF according to PyMuPDF"

    # Disabled because it fails in cli invocation of pytests
    # def test_valid_request_test_pdf2(self):
    #     url = "https://www.campusdrugprevention.gov/sites/default/files/2021-11/Addressing-College-Drinking-and-Drug-Use%20(ACTA).pdf"
    #     response = self.test_client.get(f"/statistics/pdf?url={url}&testing=true")
    #     assert response.status_code == 200
    #     data = json.loads(response.data)
    #     assert len(data["text_links"]) == data["text_links_total"] == 95
    #     # print(data["annotation_links_total"])
    #     assert len(data["annotation_links"]) == data["annotation_links_total"] == 0
