import unittest

from bs4 import Tag

from src.models.api.handlers.xhtml import XhtmlHandler
from src.models.api.job.check_url_job import UrlJob
from src.models.api.link.xhtml_link import XhtmlLink


class TestXhtmlHandler(unittest.TestCase):
    handler1 = XhtmlHandler(
        job=UrlJob(
            url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            timeout=10,
        )
    )
    handler2 = XhtmlHandler(job=UrlJob(url="https://hsivonen.com/"))
    handler3 = XhtmlHandler(
        job=UrlJob(
            url="https://www.w3.org/Style/CSS/Test/CSS3/Selectors/current/html/static/index.html"
        )
    )

    def test_extract_links1(self):
        self.handler1.download_and_extract()
        assert self.handler1.error is True
        assert (
            self.handler1.error_details
            == "Invalid content type for XHTML file. Got application/pdf; qs=0.001"
        )

    def test_extract_links2(self):
        self.handler2.download_and_extract()
        assert self.handler2.__total_number_of_links__ == 60

    def test_extract_links3(self):
        self.handler3.download_and_extract()
        assert self.handler3.__total_number_of_links__ == 0

    def test_get_dict1(self):
        self.handler2.download_and_extract()
        data = self.handler2.get_dict()
        assert "links_total" in data
        assert data["links_total"] == 60
        assert "links" in data
        assert len(data["links"]) == 60
        first_link = data["links"][0]
        # remove the Tag which causes a test error
        test_tag = Tag(name="test")
        first_link["context"] = first_link["parent"] = test_tag
        assert first_link == XhtmlLink(
            context=test_tag,
            href="https://crates.io/crates/encoding_rs",
            title="",
            parent=test_tag,
        )
        assert data["detected_language"] == "en"

    def test_get_dict2(self):
        self.handler3.download_and_extract()
        data = self.handler3.get_dict()
        assert "links_total" in data
        assert data["links_total"] == len(data["links"]) == 0
        assert data["detected_language"] == "en"
