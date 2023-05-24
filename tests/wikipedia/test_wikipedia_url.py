import logging
from unittest import TestCase

from src.models.wikimedia.wikipedia.url import WikipediaUrl

logger = logging.getLogger(__name__)


class TestWikipediaUrl(TestCase):
    archive_url1 = "https://web.archive.org/web/20220000000000*/https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2016/11/sou-20167?test=2"
    archive_url2 = "https://web.archive.org/web/20141031094104/http://collections.rmg.co.uk/collections/objects/13275.html"
    archive_url3 = "https://archive.org/details/tepitotehenuaor00thomgoog"

    valid_url = "https://en.wikipedia.org/wiki/Test"
    valid_url2 = (
        "https://books.google.com/books?id=Sj9jDwAAQBAJ&printsec=frontcover&"
        "dq=python&hl=en&newbks=1&newbks_redir=0&sa=X&ved=2ahUKEwjM5J6Z-M_xAh"
        "XOXM0KHW9sBV4Q6AEwAHoECAYQAg#v=onepage&q=python&f=false"
    )
    valid_url3 = (
        "https://web.archive.org/web/20201007025522/"
        "https://en.wikipedia.org/wiki/Python_(programming_language)"
    )
    valid_url4 = (
        "https://archive.org/details/wiki_20201007025522/"
        "https://en.wikipedia.org/wiki/Python_(programming_language)"
    )
    wikipediaurl = WikipediaUrl(url=valid_url)
    wikipediaurl2 = WikipediaUrl(url=valid_url2)
    wikipediaurl3 = WikipediaUrl(url=valid_url3)
    wikipediaurl4 = WikipediaUrl(url=valid_url4)

    def test_is_wayback_machine_url(self):
        self.assertTrue(self.wikipediaUrl3.is_wayback_machine_url)
        self.assertFalse(self.wikipediaUrl.is_wayback_machine_url)

    def test_get_first_level_domain(self):
        self.wikipediaUrl.__extract_first_level_domain__()
        assert self.wikipediaUrl.first_level_domain == "wikipedia.org"
        self.wikipediaUrl2.__extract_first_level_domain__()
        assert self.wikipediaUrl2.first_level_domain == "google.com"

    def test_fld_ip_adress(self):
        url = WikipediaUrl(url="http://127.0.0.1")
        url.extract()
        assert url.first_level_domain == "127.0.0.1"
        assert url.fld_is_ip is True

    def test_fld_ip_adress_with_path(self):
        url = WikipediaUrl(url="http://127.0.0.1/test")
        url.extract()
        assert url.first_level_domain == "127.0.0.1"
        assert url.fld_is_ip is True

    def test_extract_first_level_domain_malformed1(self):
        url = WikipediaUrl(url="127.0.0.1/test")
        url.extract()
        assert url.valid is False
        # assert url.malformed_url is True
        # assert url.malformed_url_details == MalformedUrlError.NO_NETLOC_FOUND
        # assert url.added_http_scheme_worked is True

    def test_extract_first_level_domain_malformed2(self):
        url = WikipediaUrl(url="httproe.ru/pdfs/pdf_1914.pdf")
        url.extract()
        assert url.valid is False
        #
        # assert url.malformed_url is True
        # assert url.malformed_url_details == MalformedUrlError.NO_NETLOC_FOUND
        # assert url.added_http_scheme_worked is True

    def test_extract_first_level_domain_malformed3(self):
        url = WikipediaUrl(url="httpss://www1.geocities.com/")
        url.extract()
        assert url.valid is False
        # assert url.first_level_domain == "geocities.com"
        # assert url.malformed_url is True

    def test_extract_first_level_domain_malformed4(self):
        url = WikipediaUrl(url="https://www1.geocities.")
        url.extract()
        assert url.valid is False
        #
        # assert url.malformed_url is True
        # assert url.malformed_url_details == MalformedUrlError.UNRECOGNIZED_TLD_LENGTH

    def test___check_tld__invalid(self):
        url = WikipediaUrl(url="https://www1.geocities.")
        url.extract()
        assert url.valid is False
        # url.__extract_tld__()
        # assert url.malformed_url is True
        # assert url.malformed_url_details == MalformedUrlError.UNRECOGNIZED_TLD_LENGTH

    def test___check_tld__valid(self):
        url = WikipediaUrl(url="https://www.google.com")
        url.extract()
        assert url.malformed_url is False
        assert url.valid is True

    def test___check_tld__valid_long(self):
        url = WikipediaUrl(url="https://www.easterisland.travel")
        url.extract()
        assert url.malformed_url is False

    def test_check_scheme(self):
        url = WikipediaUrl(url="http://media.hoover.org/documents/clm7_jm.pdf")
        url.extract()
        assert url.malformed_url is False

    def test__parse_wayback_machine_url__1(self):
        url = WikipediaUrl(url=self.archive_url1)
        # print(url.__get_url__)
        url.__parse_wayback_machine_url__()
        assert url.wayback_machine_timestamp == "20220000000000*"
        assert (
            url.archived_url
            == "https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2016/11/sou-20167?test=2"
        )

    def test__parse_wayback_machine_url__2(self):
        url = WikipediaUrl(url=self.archive_url2)
        # print(url.__get_url__)
        url.__parse_wayback_machine_url__()
        assert url.wayback_machine_timestamp == "20141031094104"
        assert (
            url.archived_url
            == "http://collections.rmg.co.uk/collections/objects/13275.html"
        )

    def test_fld_empty_archived_url(self):
        url = WikipediaUrl(url="https://web.archive.org/web/")
        url.extract()
        assert url.first_level_domain == "archive.org"

    def test_fld_archived_url_1(self):
        url = WikipediaUrl(url=self.archive_url1)
        url.extract()
        print(url.archived_url)
        print(url.first_level_domain)
        assert url.first_level_domain == "regeringen.se"

    def test_fld_archived_url_2(self):
        url = WikipediaUrl(url=self.archive_url2)
        url.extract()
        print(url.first_level_domain)
        assert url.first_level_domain == "rmg.co.uk"

    def test_fld_good_url(self):
        url = WikipediaUrl(url=self.valid_url)
        url.extract()
        assert url.first_level_domain == "wikipedia.org"

    def test_is_wm_url(self):
        url = WikipediaUrl(url=self.archive_url1)
        assert url.is_wayback_machine_url is True
        url = WikipediaUrl(url=self.archive_url2)
        assert url.is_wayback_machine_url is True

    def test_fld_archiveorg(self):
        url = WikipediaUrl(url="https://archive.org/details/tepitotehenuaor00thomgoog")
        url.extract()
        assert url.first_level_domain == "archive.org"

    def test_fld_germanic(self):
        url = WikipediaUrl(
            url="http://www.germanic-lexicon-project.org/texts/oi_cleasbyvigfusson_about.html"
        )
        url.extract()
        assert url.first_level_domain == "germanic-lexicon-project.org"
