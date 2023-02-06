# from __future__ import annotations
#
# import logging
# from unittest import TestCase
#
# from pydantic import ValidationError
# from wikibaseintegrator.models import Claim  # type: ignore
# from wikibaseintegrator.wbi_exceptions import MWApiError  # type: ignore
#
# import config
# from src.models.wikibase_deprecated.crud import WikibaseCrud
#
#
# logging.basicConfig(level=config.loglevel)
# logger = logging.getLogger(__name__)
#
#
# class TestWikibaseCrud(TestCase):
#     def test_entity_url(self):
#         wc = WikibaseCrud(wikibase_deprecated=IASandboxWikibase())
#         result = wc.entity_url(qid="Q1")
#         assert result == f"https://ia-sandbox.wikibase.cloud/wiki/Item:Q1"
#
#     def test_entity_url_missing_arguments(self):
#         wc = WikibaseCrud(wikibase_deprecated=IASandboxWikibase())
#         with self.assertRaises(ValidationError):
#             wc.entity_url()
#
#     # @pytest.mark.skipif(bool(getenv("CI")), reason="GitHub Actions do not have logins")
#     # def test_get_all_page_items(self):
#     #     # first import a page to make sure there is at least one to be found
#     #     bot = WcdImportBot(wikibase_deprecated=IASandboxWikibase())
#     #     # this page has no references
#     #     bot.get_and_extract_page_by_title(title="Test")
#     #     console.print(
#     #         f"Waiting {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
#     #     )
#     #     sleep(config.sparql_sync_waiting_time_in_seconds)
#     #     wikibase_deprecated = IASandboxWikibase()
#     #     wcr = WikibaseCrudRead(wikibase_deprecated=wikibase_deprecated)
#     #     result = wcr.__get_all_items__(item_type=wikibase_deprecated.WIKIPEDIA_PAGE)
#     #     console.print(result)
#     #     assert len(result) > 0
#     #     # bot.rinse_all_items_and_cache()
#     #     # exit()
#     #     # items = wc.__get_all_page_items__()
#     #     # if items is None or len(items) == 0:
#     #     #     self.fail("Got no items")
#     #
#     # @pytest.mark.skipif(bool(getenv("CI")), reason="GitHub Actions do not have logins")
#     # def test_get_all_reference_items(self):
#     #     # first import a page with at least one reference
#     #     # to make sure there is at least one to be found
#     #     bot = WcdImportBot(wikibase_deprecated=IASandboxWikibase())
#     #     # this page has no references
#     #     bot.get_and_extract_page_by_title(title="Muskö naval base")
#     #     console.print(
#     #         f"Waiting {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
#     #     )
#     #     sleep(config.sparql_sync_waiting_time_in_seconds)
#     #     wcr = WikibaseCrudRead(wikibase_deprecated=IASandboxWikibase())
#     #     result = wcr.__get_all_items__(item_type=IASandboxWikibase().WIKIPEDIA_REFERENCE)
#     #     # console.print(result)
#     #     assert len(result) > 0
#     #     # bot.rinse_all_items_and_cache()
#     #     # exit()
#     #     # items = wc.__get_all_page_items__()
#     #     # if items is None or len(items) == 0:
#     #     #     self.fail("Got no items")
#
#
# # def test_P19_claims(self):
# #     site = pywikibot.Site(code="en", fam=WikimediaSite.WIKIPEDIA.value)
# #
# #     page = WikipediaArticle(
# #         pywikibot_site=site,
# #         language_code="en",
# #         wikimedia_site=WikimediaSite.WIKIPEDIA,
# #         # max_number_of_item_citations_to_upload=1,
# #     )
# #     page.__get_wikipedia_article_from_title__(title="Culture change")
# #     page.extract_and_upload_to_WikiCitations(wikibase_deprecated=IASandboxWikibase())
#
# # def test_delete_all_page_items(self):
# #     wc = WikiCitations(
# #         wikibase_deprecated=IASandboxWikibase()
# #     )
# #     wc.__delete_all_page_items__()
# #
# # def test_delete_all_reference_items(self):
# #     wc = WikiCitations(
# #         wikibase_deprecated=IASandboxWikibase()
# #     )
# #     wc.__delete_all_reference_items__()
