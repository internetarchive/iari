from unittest import TestCase

from src.helpers.console import console
from src.models.api.lookup_by_wikidata_qid import LookupByWikidataQid


class TestLookupByWikidataQid(TestCase):
    """these tests rely on lookups to WDQS"""
    def test_get_empty(self):
        lookup = LookupByWikidataQid()
        result = lookup.get(qid="")
        # print(type(result))
        # console.print(result)
        assert result[1] == 400

    def test_get_valid(self):
        lookup = LookupByWikidataQid()
        result = lookup.get(qid="Q14452", testing=True) # easter island
        # print(type(result))
        console.print(result)
        assert result == "Q2680"

    def test_get_invalid(self):
        lookup = LookupByWikidataQid()
        result = lookup.get(qid="14452", testing=True)
        # print(type(result))
        console.print(result)
        assert result[1] == 400

    def test_get_not_found(self):
        lookup = LookupByWikidataQid()
        result = lookup.get(qid="Q1445200000000", testing=True)
        # print(type(result))
        console.print(result)
        assert result[1] == 404
