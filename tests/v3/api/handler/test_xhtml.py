import unittest

from bs4 import Tag

from src.v2.models.api.handlers.xhtml import XhtmlHandler
from src.v2.models.api.job.check_url_job import UrlJob
from src.v2.models.api.link.xhtml_link import XhtmlLink


class TestXhtmlHandler(unittest.TestCase):
    pdf_handler1 = XhtmlHandler(
        job=UrlJob(
            url="https://www.campusdrugprevention.gov/sites/default/files/2021-11/Addressing-College-Drinking-and-Drug-Use%20(ACTA).pdf",
            timeout=10,
        )
    )
    pdf_handler2 = XhtmlHandler(
        job=UrlJob(url="https://hsivonen.com/test/xhtml-suite/xhtml11.xhtml")
    )
    pdf_handler3 = XhtmlHandler(
        job=UrlJob(
            url="https://www.w3.org/Style/CSS/Test/CSS3/Selectors/current/html/static/index.html"
        )
    )

    def test_extract_links1(self):
        self.pdf_handler1.download_and_extract()
        assert self.pdf_handler1.error is True
        assert (
            self.pdf_handler1.error_details
            == "Invalid content type for XHTML file. Got application/pdf"
        )

    def test_extract_links2(self):
        self.pdf_handler2.download_and_extract()
        assert self.pdf_handler2.total_number_of_links == 2

    def test_extract_links3(self):
        self.pdf_handler3.download_and_extract()
        assert self.pdf_handler3.total_number_of_links == 13

    def test_get_dict1(self):
        self.pdf_handler2.download_and_extract()
        data = self.pdf_handler2.get_dict()
        assert "links_total" in data
        assert data["links_total"] == 2
        assert "links" in data
        assert len(data["links"]) == 2
        first_link = data["links"][0]
        # remove the Tag which causes a test error
        test_tag = Tag(name="test")
        first_link["context"] = first_link["parent"] = test_tag
        assert first_link == XhtmlLink(
            context=test_tag,
            href="http://www.hut.fi/u/hsivonen/test/xhtml-suite/",
            title="The main page of this test suite",
            parent=test_tag,
        )

    def test_get_dict2(self):
        self.pdf_handler3.download_and_extract()
        data = self.pdf_handler3.get_dict()
        assert "links_total" in data
        assert data["links_total"] == len(data["links"]) == 13
        first_link = data["links"][0]
        # remove the Tag which causes a test error
        test_tag = Tag(name="test")
        first_link["context"] = first_link["parent"] = test_tag
        assert first_link == XhtmlLink(
            context=test_tag,
            href="flat/index.html",
            title="",
            parent=test_tag,
        )
