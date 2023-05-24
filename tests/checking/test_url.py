from unittest import TestCase

from src.models.identifiers_checking.url import Url


class TestUrl(TestCase):
    no_url = ""
    good_url = "https://www.easterisland.travel"
    bad_url = "ht.test..."
    bad_url2 = "ht.testtretdrgd"
    forbidden_url_if_not_spoofed_headers = (
        "https://www.sciencedaily.com/releases/2021/07/210713090153.htm"
    )

    def test_check_good(self):
        url = Url(url=self.good_url, timeout=2)
        url.check()
        assert url.status_code == 200
        assert url.malformed_url is False
        assert url.request_error is False
        assert url.response_headers != {}
        assert url.response_headers["Server"] == "Apache"

    def test_check_no(self):
        url = Url(url=self.no_url, timeout=2)
        url.check()
        assert url.status_code == 0
        assert url.malformed_url is False
        assert url.response_headers == {}

    def test_check_bad_dots(self):
        url = Url(url=self.bad_url, timeout=2)
        url.check()
        assert url.is_valid is False
        # assert url.status_code == 0
        # # assert url.dns_error is True
        # assert url.request_error is True
        # assert (
        #     url.request_error_details
        #     == "Failed to parse: 'ht.test...', label empty or too long"
        # )
        # assert url.response_headers == {}

    def test_check_bad_long_tld(self):
        url = Url(url=self.bad_url2, timeout=2)
        url.check()
        assert url.is_valid is False
        # assert url.status_code == 0
        # assert url.malformed_url is True
        # assert url.dns_error is False
        # assert url.request_error is True
        # assert url.request_error_details[:100] == (
        #     "HTTPConnectionPool(host='ht.testtretdrgd', port=80): "
        #     "Max retries exceeded with url: / (Caused by New"
        # )
        # assert url.response_headers == {}

    def test_check_403(self):
        url = Url(url=self.forbidden_url_if_not_spoofed_headers, timeout=2)
        url.check()
        assert url.status_code == 200
        assert url.dns_error is False
        assert url.request_error is False
        assert url.malformed_url is False
        assert url.response_headers["Server"] == "AmazonS3"

    def test_check_response_header(self):
        url = Url(url=self.good_url, timeout=2)
        url.check()
        assert url.status_code == 200
        assert url.response_headers != {}
        assert url.malformed_url is False
        assert url.response_headers["Server"] == "Apache"

    def test_alternating_status_code_url(self):
        url = Url(
            url="https://web.archive.org/web/20111026115104/http://scholarspace."
            "manoa.hawaii.edu/handle/10125/6262",
            timeout=60,
        )
        url.check()
        assert url.status_code == 200
        assert url.dns_error is False
        assert url.request_error is False
        assert url.malformed_url is False

    def test_wm_url(self):
        url = Url(
            url="https://web.archive.org/web/20110328065358/http://www.amazon.com/",
            timeout=60,
        )
        url.check()
        assert url.first_level_domain == "amazon.com"
        assert url.status_code == 200
        assert url.dns_error is False
        assert url.request_error is False
        assert url.malformed_url is False
