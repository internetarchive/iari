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
        self.wikipediaUrl.fix_and_check()
        self.assertEqual(self.wikipediaUrl.status_code, 200)
        self.assertTrue(self.wikipediaUrl.checked)

    def test_check_200_wm(self):
        url = WikipediaUrl(url="http://web.archive.org")
        url.fix_and_check()
        assert url.status_code == 200

    def test_check_404(self):
        invalid_url = "https://en.wikipedia.org/wiki/45q2345awf"
        invalid = WikipediaUrl(url=invalid_url)
        invalid.fix_and_check()
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

    def test___fix_malformed_httpswww__(self):
        url = WikipediaUrl(url="httpswww.quarryhs.co.uk/GRENADES%20WEB%20ARTICLE.pdf")
        url.__fix_malformed_httpswww__()
        assert url.url == "https://www.quarryhs.co.uk/GRENADES%20WEB%20ARTICLE.pdf"

    def test___fix_malformed_httpwww__(self):
        url = WikipediaUrl(url="httpwww.quarryhs.co.uk/GRENADES%20WEB%20ARTICLE.pdf")
        url.__fix_malformed_httpwww__()
        assert url.url == "http://www.quarryhs.co.uk/GRENADES%20WEB%20ARTICLE.pdf"

    def test___netloc__no_scheme(self):
        url = WikipediaUrl(url="httproe.ru/pdfs/pdf_1914.pdf")
        assert url.__netloc__ == "httproe.ru"

    def test___netloc__with_scheme(self):
        url = WikipediaUrl(
            url="http://news.oneindia.in/2010/10/21/india-invents-laser-guide-bomb.html"
        )
        assert url.__netloc__ == "news.oneindia.in"

    def test_check_dns_false(self):
        url = WikipediaUrl(
            url="http://news.oneindia.in/2010/10/21/india-invents-laser-guide-bomb.html"
        )
        assert url.__dns_record_found__ is False

    def test_check_dns_true(self):
        url = WikipediaUrl(url="http://www.google.com")
        assert url.__dns_record_found__ is True

    def test_error1(self):
        url = WikipediaUrl(url="https://voyagermediaawards.nz/judges2019")
        url.fix_and_check()
        assert url.timeout_or_retry_error is True

    def test_error2(self):
        url = WikipediaUrl(url="https://ukrainianweek.com/History/198459")
        url.fix_and_check()
        assert url.timeout_or_retry_error is True

    def test_ssl_error(self):
        url = WikipediaUrl(
            url="https://www.orbitalatk.com/defense-systems/armament-systems/cdte/"
        )
        url.fix_and_check()
        assert url.ssl_error is True

    def test_status_code_404(self):
        url = WikipediaUrl(
            url="https://www.orbitalatk.com/defense-systems/armament-systems/cdte/"
        )
        url.fix_and_check()
        assert url.status_code == 404
        assert url.checked is True

    def test_no_dns(self):
        url = WikipediaUrl(url="https://www1.geocities.com/")
        url.fix_and_check()
        assert url.no_dns_record is True
        assert url.checked is True

    # def test_check_soft404(self):
    #     assert False
    #
