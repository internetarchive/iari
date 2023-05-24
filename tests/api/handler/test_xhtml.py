import unittest

from src.models.api.handlers.xhtml import XhtmlHandler
from src.models.api.job.check_url_job import UrlJob


class TestXhtmlHandler(unittest.TestCase):
    handler1 = XhtmlHandler(
        job=UrlJob(
            url="https://www.campusdrugprevention.gov/sites/default/files/2021-11/Addressing-College-Drinking-and-Drug-Use%20(ACTA).pdf",
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
            == "Invalid content type for XHTML file. Got application/pdf"
        )

    def test_extract_links2(self):
        self.handler2.download_and_extract()
        assert self.handler2.total_number_of_links == 60

    def test_extract_links3(self):
        self.handler3.download_and_extract()
        assert self.handler3.total_number_of_links == 0

    # TODO rewrite these tests after merging the validator check
    # def test_get_dict1(self):
    #     self.handler2.download_and_extract()
    #     data = self.handler2.get_dict()
    #     assert "links_total" in data
    #     assert data["links_total"] == 265
    #     assert "links" in data
    #     assert len(data["links"]) == 265
    #     first_link = data["links"][0]
    #     # remove the Tag which causes a test error
    #     test_tag = Tag(name="test")
    #     first_link["context"] = first_link["parent"] = test_tag
    #     assert first_link == XhtmlLink(
    #         context=test_tag,
    #         href="http://www.hut.fi/u/hsivonen/test/xhtml-suite/",
    #         title="The main page of this test suite",
    #         parent=test_tag,
    #     )

    # def test_get_dict2(self):
    #     self.handler3.download_and_extract()
    #     data = self.handler3.get_dict()
    #     assert "links_total" in data
    #     assert data["links_total"] == len(data["links"]) == 13
    #     first_link = data["links"][0]
    #     # remove the Tag which causes a test error
    #     test_tag = Tag(name="test")
    #     first_link["context"] = first_link["parent"] = test_tag
    #     assert first_link == XhtmlLink(
    #         context=test_tag,
    #         href="flat/index.html",
    #         title="",
    #         parent=test_tag,
    #     )
