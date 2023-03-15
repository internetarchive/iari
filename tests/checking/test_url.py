from src.models.identifiers_checking.url import Url


class TestUrl:
    no_url = ""
    good_url = "https://www.easterisland.travel"
    bad_url = "ht.test..."

    def test_check_good(self):
        url = Url(url=self.good_url, timeout=2)
        url.check()
        assert url.status_code == 200

    def test_check_no(self):
        url = Url(url=self.no_url, timeout=2)
        url.check()
        assert url.status_code == 0

    def test_check_bad(self):
        url = Url(url=self.bad_url, timeout=2)
        url.check()
        assert url.status_code == 0
        assert url.dns_error is True and url.request_error is True

    # def test_get_dict(self):
    #     assert False
