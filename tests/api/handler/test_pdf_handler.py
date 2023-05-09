import os
import unittest

import pytest

from src.models.api.handlers.pdf import PdfHandler
from src.models.api.job.check_url_job import UrlJob


class TestPdfHandler(unittest.TestCase):
    pdf_handler2 = PdfHandler(
        job=UrlJob(url="https://s1.q4cdn.com/806093406/files/doc_downloads/test.pdf")
    )
    pdf_handler3 = PdfHandler(
        job=UrlJob(
            url="https://www.foundationforfreedomonline.com/wp-content/uploads/2023/03/FFO-FLASH-REPORT-REV.pdf"
        )
    )

    def test_extract_links1(self):
        pdf_handler1 = PdfHandler(
            job=UrlJob(
                url="https://www.campusdrugprevention.gov/sites/default/files/2021-11/Addressing-College-Drinking-and-Drug-Use%20(ACTA).pdf",
                timeout=10,
            )
        )
        pdf_handler1.download_and_extract()
        assert pdf_handler1.number_of_text_links == 95

    def test_extract_links2(self):
        self.pdf_handler2.download_and_extract()
        assert self.pdf_handler2.number_of_text_links == 0

    def test_get_dict1(self):
        pdf_handler1 = PdfHandler(
            job=UrlJob(
                url="https://www.campusdrugprevention.gov/sites/default/files/2021-11/Addressing-College-Drinking-and-Drug-Use%20(ACTA).pdf",
                timeout=10,
            )
        )
        pdf_handler1.download_and_extract()
        data = pdf_handler1.get_dict()
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
        pdf_handler = PdfHandler(
            job=UrlJob(url=""),
            testing=True,
            file_path="../test_data/mwg-fdr-document-04-16-23-1-270.pdf",
        )
        pdf_handler.read_pdf_from_file()
        assert pdf_handler.content != b""
        pdf_handler.__extract_pages_and_links__()
        assert pdf_handler.number_of_pages == 1
        # print(pdf_handler.__get_cleaned_page_string__(number=0))
        assert pdf_handler.number_of_text_links == 14
        links = pdf_handler.all_text_links
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
        pdf_handler = PdfHandler(
            job=UrlJob(url=""),
            testing=True,
            file_path="../test_data/mwg-fdr-document-04-16-23-1-270.pdf",
        )
        pdf_handler.read_pdf_from_file()
        pdf_handler.__extract_pdf_document__()
        pdf_handler.__extract_links_from_annotations__()
        assert pdf_handler.number_of_annotation_links == 14

    def test_extract_links_same_number_found(self):
        pdf_handler = PdfHandler(
            job=UrlJob(url=""),
            testing=True,
            file_path="../test_data/mwg-fdr-document-04-16-23-1-270.pdf",
        )
        pdf_handler.read_pdf_from_file()
        pdf_handler.__extract_pages_and_links__()
        assert (
            pdf_handler.number_of_annotation_links
            == pdf_handler.number_of_text_links
            == 14
        )

    def test_extracted_links_are_identical(self):
        pdf_handler = PdfHandler(
            job=UrlJob(url=""),
            testing=True,
            file_path="../test_data/mwg-fdr-document-04-16-23-1-270.pdf",
        )
        pdf_handler.read_pdf_from_file()
        pdf_handler.__extract_pages_and_links__()
        assert pdf_handler.annotation_links == pdf_handler.annotation_links
