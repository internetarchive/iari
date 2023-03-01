# from unittest import TestCase
#
# from src import IASandboxWikibase
# from src.models.wikibase.wikicitations_wikibase import WikiCitationsWikibase
#
#
# class TestWikibase(TestCase):
#     def test_valid_qid_invalid_input(self):
#         """We instantiate WikiCitationsWikibase here but the methods are inherited from Wikibase"""
#         wcw = WikiCitationsWikibase()
#         assert wcw.is_valid_qid(qid="123") is False
#
#     def test_valid_qid_valid_input(self):
#         """We instantiate WikiCitationsWikibase here but the methods are inherited from Wikibase"""
#         wcw = WikiCitationsWikibase()
#         assert wcw.is_valid_qid(qid="Q123") is True
#
#     def test_valid_qid_valid_input_lowercase(self):
#         """We instantiate WikiCitationsWikibase here but the methods are inherited from Wikibase"""
#         wcw = WikiCitationsWikibase()
#         assert wcw.is_valid_qid(qid="q123") is True
#
#     def test_valid_qid_invalid_input_alpha(self):
#         """We instantiate WikiCitationsWikibase here but the methods are inherited from Wikibase"""
#         wcw = WikiCitationsWikibase()
#         assert wcw.is_valid_qid(qid="q123a") is False
#
#     def test_wcd_urls(self):
#         wcw = WikiCitationsWikibase()
#         assert (
#             wcw.sparql_endpoint_url
#             == "https://wikicitations.wikibase.cloud/query/sparql"
#         )
#         assert wcw.wikibase_url == "https://wikicitations.wikibase.cloud/"
#         assert (
#             wcw.entity_url(item_id="Q1")
#             == "https://wikicitations.wikibase.cloud/wiki/Item:Q1"
#         )
#         assert (
#             wcw.entity_history_url(item_id="Q1")
#             == "https://wikicitations.wikibase.cloud/w/index.php?title=Item:Q1&action=history"
#         )
#         assert wcw.rdf_prefix_url == "https://wikicitations.wikibase.cloud/"
#         assert (
#             wcw.rdf_entity_prefix_url == "https://wikicitations.wikibase.cloud/entity/"
#         )
#         assert (
#             wcw.rdf_prefix_prop_direct_url
#             == "https://wikicitations.wikibase.cloud/prop/direct/"
#         )
#
#     def test_sandbox_urls(self):
#         wcw = IASandboxWikibase()
#         assert (
#             wcw.sparql_endpoint_url == "https://ia-sandbox.wikibase.cloud/query/sparql"
#         )
#         assert wcw.wikibase_url == "https://ia-sandbox.wikibase.cloud/"
#         assert (
#             wcw.entity_url(item_id="Q1")
#             == "https://ia-sandbox.wikibase.cloud/wiki/Item:Q1"
#         )
#         assert (
#             wcw.entity_history_url(item_id="Q1")
#             == "https://ia-sandbox.wikibase.cloud/w/index.php?title=Item:Q1&action=history"
#         )
#         assert wcw.rdf_prefix_url == "https://ia-sandbox.wikibase.cloud/"
#         assert wcw.rdf_entity_prefix_url == "https://ia-sandbox.wikibase.cloud/entity/"
#         assert (
#             wcw.rdf_prefix_prop_direct_url
#             == "https://ia-sandbox.wikibase.cloud/prop/direct/"
#         )
