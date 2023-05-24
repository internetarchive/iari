import os
import unittest

import pytest

from src.models.api.handlers.pdf import PdfHandler
from src.models.api.job.check_url_job import UrlJob


class TestPdfHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.pdf_handler1 = PdfHandler(
            job=UrlJob(url=""),
            testing=True,
            file_path="test_data/Addressing-College-Drinking-and-Drug-Use.pdf",
        )
        self.pdf_handler1.read_and_extract()
        self.pdf_handler2 = PdfHandler(
            job=UrlJob(url=""),
            testing=True,
            file_path="test_data/test.pdf",
        )
        self.pdf_handler2.read_and_extract()
        self.pdf_handler3 = PdfHandler(
            job=UrlJob(url=""),
            testing=True,
            file_path="test_data/FFO-FLASH-REPORT-REV.pdf",
        )
        self.pdf_handler3.read_and_extract()
        self.pdf_handler4 = PdfHandler(
            job=UrlJob(url=""),
            testing=True,
            file_path="test_data/mwg-fdr-document-04-16-23-1-270.pdf",
        )
        self.pdf_handler4.read_and_extract()

    def test_extract_links1(self):
        assert self.pdf_handler1.number_of_text_links == 95

    def test_extract_links2(self):
        assert self.pdf_handler2.number_of_text_links == 0

    def test_get_dict1(self):
        data = self.pdf_handler1.get_dict()
        # console.print(data)
        assert data["annotation_links_total"] == 0
        assert data["text_links_total"] == 95
        assert data["text_links"][0] == {
            "page": 30,
            "url": "https://www.chronicle.com/resource/alcohol-s-influence-on-campus/6113/.Berenson,",
        }

    @pytest.mark.skipif(
        "GITHUB_ACTIONS" in os.environ, reason="test is skipped in GitHub Actions"
    )
    def test_incomplete_link_dni(self):
        assert self.pdf_handler4.content != b""
        assert self.pdf_handler4.number_of_pages == 1
        # print(pdf_handler.__get_cleaned_page_string__(number=0))
        assert self.pdf_handler4.number_of_text_links == 14
        links = self.pdf_handler4.all_text_links
        # print(pdf_handler.links)
        assert (
            links[1].url
            == "https://www.dni.gov/files/ODNI/documents/assessments/Declassified-Assessment-on-COVID-19-Origins.pdf"
        )
        assert (
            links[2].url
            == "https://gop-foreignaffairs.house.gov/wp-content/uploads/2021/08/ORIGINS-OF-COVID-19-REPORT.pdf"
        )

    def test___extract_links_from_annotations__(self):
        assert self.pdf_handler4.number_of_annotation_links == 14

    def test_extract_links_same_number_found(self):
        assert (
            self.pdf_handler4.number_of_annotation_links
            == self.pdf_handler4.number_of_text_links
            == 14
        )

    def test_extracted_links_are_identical(self):
        assert self.pdf_handler4.annotation_links == self.pdf_handler4.annotation_links

    def test_mean_max_min_words(self):
        # print(self.pdf_handler4.mean_number_of_words_per_page, self.pdf_handler4.min_number_of_words_per_page, self.pdf_handler4.max_number_of_words_per_page)
        assert (
            self.pdf_handler4.mean_number_of_words_per_page
            == 461
            == self.pdf_handler4.min_number_of_words_per_page
            == self.pdf_handler4.max_number_of_words_per_page
        )

    def test_mean_max_min_words2(self):
        # print(self.pdf_handler1.mean_number_of_words_per_page, self.pdf_handler1.min_number_of_words_per_page, self.pdf_handler1.max_number_of_words_per_page)
        assert self.pdf_handler1.mean_number_of_words_per_page == 344
        assert self.pdf_handler1.min_number_of_words_per_page == 0
        assert self.pdf_handler1.max_number_of_words_per_page == 578

    def test_dict1(self):
        data = self.pdf_handler1.get_dict()
        assert data["detected_language"] == "en"
        assert data["detected_language_error"] is False

    def test_dict2(self):
        data = self.pdf_handler2.get_dict()
        assert data["detected_language"] == ""
        assert data["detected_language_error"] is True
        assert (
            data["detected_language_error_details"]
            == "Not enough text for us to reliably detect the language"
        )
