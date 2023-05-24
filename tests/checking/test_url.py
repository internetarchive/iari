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
    archive_url1 = "https://web.archive.org/web/20220000000000*/https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2016/11/sou-20167?test=2"
    archive_url2 = "https://web.archive.org/web/20141031094104/http://collections.rmg.co.uk/collections/objects/13275.html"

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
        assert url.status_code == 0
        assert url.malformed_url is True
        assert url.dns_error is True and url.request_error is True
        assert (
            url.request_error_details
            == "Failed to parse: 'ht.test...', label empty or too long"
        )
        assert url.response_headers == {}

    def test_check_bad_long_tld(self):
        url = Url(url=self.bad_url2, timeout=2)
        url.check()
        assert url.status_code == 0
        assert url.malformed_url is True
        assert url.dns_error is False
        assert url.request_error is True
        assert url.request_error_details[:100] == (
            "HTTPConnectionPool(host='ht.testtretdrgd', port=80): "
            "Max retries exceeded with url: / (Caused by New"
        )
        assert url.response_headers == {}

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

    def test_wm_urls(self):
        url = Url(
            url="https://web.archive.org/web/20110328065358/http://www.amazon.com/",
            timeout=60,
        )
        url.check()
        assert url.status_code == 200
        assert url.dns_error is False
        assert url.request_error is False
        assert url.malformed_url is False

    def test__parse_wayback_machine_url__1(self):
        url = Url(url=self.archive_url1)
        print(url.__get_url__)
        url.__parse_wayback_machine_url__()
        assert url.wayback_machine_timestamp == "20220000000000*"
        assert (
            url.archived_url
            == "https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2016/11/sou-20167?test=2"
        )

    def test__parse_wayback_machine_url__2(self):
        url = Url(url=self.archive_url2)
        print(url.__get_url__)
        url.__parse_wayback_machine_url__()
        assert url.wayback_machine_timestamp == "20141031094104"
        assert (
            url.archived_url
            == "http://collections.rmg.co.uk/collections/objects/13275.html"
        )

    def test_fld_empty_archived_url(self):
        url = Url(url="https://web.archive.org/web/")
        url.__get_fld__()
        assert url.first_level_domain == "archive.org"

    def test_fld_archived_url_1(self):
        url = Url(url=self.archive_url1)
        url.__get_fld__()
        self.assertEqual(url.wayback_machine_timestamp, "")
        self.assertEqual(url.archived_url, "")

    def test_fld_archived_url_2(self):
        url = Url(url=self.archive_url2)
        url.__get_fld__()
        self.assertEqual(url.wayback_machine_timestamp, "")
        self.assertEqual(url.archived_url, "")

    def test_fld_good_url(self):
        url = Url(url=self.good_url)
        url.__get_fld__()
        self.assertEqual(url.wayback_machine_timestamp, "")
        self.assertEqual(url.archived_url, "")
