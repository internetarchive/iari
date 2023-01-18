import logging
from unittest import TestCase

from src.models.wikimedia.wikipedia.url import WikipediaUrl

logger = logging.getLogger(__name__)


class TestWikipediaUrl(TestCase):
    def setUp(self):
        self.valid_url = "https://en.wikipedia.org/wiki/Test"
        self.valid_url2 = (
            "https://books.google.com/books?id=Sj9jDwAAQBAJ&printsec=frontcover&"
            "dq=python&hl=en&newbks=1&newbks_redir=0&sa=X&ved=2ahUKEwjM5J6Z-M_xAh"
            "XOXM0KHW9sBV4Q6AEwAHoECAYQAg#v=onepage&q=python&f=false"
        )
        self.valid_url3 = (
            "https://web.archive.org/web/20201007025522/"
            "https://en.wikipedia.org/wiki/Python_(programming_language)"
        )
        self.valid_url4 = (
            "https://archive.org/details/wiki_20201007025522/"
            "https://en.wikipedia.org/wiki/Python_(programming_language)"
        )
        self.wikipediaUrl = WikipediaUrl(url=self.valid_url)
        self.wikipediaUrl2 = WikipediaUrl(url=self.valid_url2)
        self.wikipediaUrl3 = WikipediaUrl(url=self.valid_url3)
        self.wikipediaUrl4 = WikipediaUrl(url=self.valid_url4)

    # def mocked_requests_get(self):
    #     class MockResponse:
    #         def __init__(self, status_code):
    #             self.status_code = status_code
    #
    #     return MockResponse(200)

    def test_check_200(self):
        self.wikipediaUrl.check()
        self.assertEqual(self.wikipediaUrl.status_code, 200)
        self.assertTrue(self.wikipediaUrl.checked)

    def test_check_404(self):
        invalid_url = "https://en.wikipedia.org/wiki/45q2345awf"
        invalid = WikipediaUrl(url=invalid_url)
        invalid.check()
        self.assertEqual(404, invalid.status_code)
        self.assertTrue(invalid.checked)

    def test_is_google_books_url(self):
        self.assertTrue(self.wikipediaUrl2.is_google_books_url())
        self.assertFalse(self.wikipediaUrl.is_google_books_url())

    def test_is_wayback_machine_url(self):
        self.assertTrue(self.wikipediaUrl3.is_wayback_machine_url())
        self.assertFalse(self.wikipediaUrl.is_wayback_machine_url())

    def test_is_ia_details_url(self):
        self.assertTrue(self.wikipediaUrl4.is_ia_details_url())
        self.assertFalse(self.wikipediaUrl.is_ia_details_url())

    def test_get_first_level_domain(self):
        self.wikipediaUrl.get_first_level_domain()
        assert self.wikipediaUrl.first_level_domain == "wikipedia.org"
        self.wikipediaUrl2.get_first_level_domain()
        assert self.wikipediaUrl2.first_level_domain == "google.com"

    # def test_check_soft404(self):
    #     assert False
    #
