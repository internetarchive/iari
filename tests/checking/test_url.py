from src.models.identifiers_checking.url import Url


class TestUrl:
    no_url = ""
    good_url = "https://www.easterisland.travel"
    bad_url = "ht.test..."
    forbidden_url_if_not_spoofed_headers = (
        "https://www.sciencedaily.com/releases/2021/07/210713090153.htm"
    )

    def test_check_good(self):
        url = Url(url=self.good_url, timeout=2)
        url.check()
        assert url.status_code == 200
        assert url.response_headers != {}
        assert url.response_headers["Server"] == "Apache"

    def test_check_no(self):
        url = Url(url=self.no_url, timeout=2)
        url.check()
        assert url.status_code == 0
        assert url.response_headers == {}

    def test_check_bad(self):
        url = Url(url=self.bad_url, timeout=2)
        url.check()
        assert url.status_code == 0
        assert url.dns_error is True and url.request_error is True
        assert url.response_headers == {}

    def test_check_403(self):
        url = Url(url=self.forbidden_url_if_not_spoofed_headers, timeout=2)
        url.check()
        assert url.status_code == 200
        assert url.response_headers["Server"] == "AmazonS3"

    def test_check_response_header(self):
        url = Url(url=self.good_url, timeout=2)
        url.check()
        assert url.status_code == 200
        assert url.response_headers != {}
        assert url.response_headers["Server"] == "Apache"