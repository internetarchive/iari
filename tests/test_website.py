# from unittest import TestCase
#
# from src import IASandboxWikibase
# from src.models.wikibase_deprecated.website import Website
# from src.models.wikimedia.wikipedia.article import WikipediaArticle
# from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference
#
#
# class TestWebsite(TestCase):
#     def test___insert_website_in_cache__(self):
#         wikibase_deprecated = IASandboxWikibase()
#         r = WikipediaReference(
#             template_name="test", url="http://test.com", wikibase_deprecated=wikibase_deprecated
#         )
#         r.finish_parsing_and_generate_hash(testing=True)
#         w = Website(reference=r)
#         w.__insert_website_in_cache__(wcdqid="test", testing=True)
#
#     def test___upload_website_to_wikibase__(self):
#         wikibase_deprecated = IASandboxWikibase()
#         r = WikipediaReference(
#             template_name="test", url="http://test.com", wikibase_deprecated=wikibase_deprecated
#         )
#         r.finish_parsing_and_generate_hash(testing=True)
#         w = Website(reference=r)
#         return_ = w.__upload_website_to_wikibase__(
#             wikipedia_article=WikipediaArticle(wikibase_deprecated=wikibase_deprecated)
#         )
#         assert return_.item_qid == "Q263"
#
#     def test_check_and_upload_website_item_to_wikibase_if_missing(self):
#         wikibase_deprecated = IASandboxWikibase()
#         r = WikipediaReference(
#             template_name="test",
#             url="http://test.com",
#             wikibase_deprecated=wikibase_deprecated
#             # first_level_domain_of_url="test.test"
#         )
#         r.finish_parsing_and_generate_hash(testing=True)
#         # r.__setup_cache__()
#         w = Website(
#             reference=r,
#             wikibase_deprecated=wikibase_deprecated,
#         )
#         wa = WikipediaArticle()
#         wa.wikibase_deprecated = wikibase_deprecated
#         w.check_and_upload_website_item_to_wikibase_if_missing(
#             wikipedia_article=wa, testing=True
#         )
#
#     def test_get_website_wcdqid_from_cache(self):
#         wikibase_deprecated = IASandboxWikibase()
#         r = WikipediaReference(
#             template_name="test",
#             url="http://test.com",
#             wikibase_deprecated=wikibase_deprecated
#             # first_level_domain_of_url="test.test"
#         )
#         r.finish_parsing_and_generate_hash(testing=True)
#         w = Website(
#             reference=r,
#         )
#         w.get_website_wcdqid_from_cache(testing=True)
#
#     def test_upload_website_and_insert_in_the_cache(self):
#         wikibase_deprecated = IASandboxWikibase()
#         r = WikipediaReference(
#             template_name="test",
#             url="http://test.com",
#             wikibase_deprecated=wikibase_deprecated
#             # first_level_domain_of_url="test.test"
#         )
#         r.finish_parsing_and_generate_hash(testing=True)
#         w = Website(
#             reference=r,
#         )
#         w.__upload_website_and_insert_in_the_cache__(
#             wikipedia_article=WikipediaArticle(wikibase_deprecated=wikibase_deprecated), testing=True
#         )
