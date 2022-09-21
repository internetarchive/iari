from unittest import TestCase

from src import IASandboxWikibase
from src.models.wikibase.website import Website
from src.models.wikimedia.wikipedia.references.wikipedia import WikipediaReference
from src.models.wikimedia.wikipedia.wikipedia_article import WikipediaArticle


class TestWebsite(TestCase):
    def test___insert_website_in_cache__(self):
        wikibase = IASandboxWikibase()
        r = WikipediaReference(
            template_name="test", url="http://test.com", wikibase=wikibase
        )
        r.finish_parsing_and_generate_hash()
        w = Website(reference=r)
        w.__insert_website_in_cache__(wcdqid="test")

    def test___upload_website_to_wikibase__(self):
        wikibase = IASandboxWikibase()
        r = WikipediaReference(
            template_name="test", url="http://test.com", wikibase=wikibase
        )
        r.finish_parsing_and_generate_hash()
        w = Website(
            reference=r,
        )
        return_ = w.__upload_website_to_wikibase__(
            wikipedia_article=WikipediaArticle(wikibase=wikibase)
        )
        assert return_.item_qid == "Q263"

    def test_check_and_upload_website_item_to_wikibase_if_missing(self):
        wikibase = IASandboxWikibase()
        r = WikipediaReference(
            template_name="test",
            url="http://test.com",
            wikibase=wikibase
            # first_level_domain_of_url="test.test"
        )
        r.finish_parsing_and_generate_hash()
        w = Website(
            reference=r,
            wikibase=wikibase,
        )
        w.check_and_upload_website_item_to_wikibase_if_missing(
            wikipedia_article=WikipediaArticle()
        )

    def test_get_website_wcdqid_from_cache(self):
        wikibase = IASandboxWikibase()
        r = WikipediaReference(
            template_name="test",
            url="http://test.com",
            wikibase=wikibase
            # first_level_domain_of_url="test.test"
        )
        r.finish_parsing_and_generate_hash()
        w = Website(
            reference=r,
        )
        w.get_website_wcdqid_from_cache()

    def test_upload_website_and_insert_in_the_cache(self):
        wikibase = IASandboxWikibase()
        r = WikipediaReference(
            template_name="test",
            url="http://test.com",
            wikibase=wikibase
            # first_level_domain_of_url="test.test"
        )
        r.finish_parsing_and_generate_hash()
        w = Website(
            reference=r,
        )
        w.__upload_website_and_insert_in_the_cache__(
            wikipedia_article=WikipediaArticle(wikibase=wikibase)
        )
