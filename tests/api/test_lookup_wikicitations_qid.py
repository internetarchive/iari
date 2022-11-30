from unittest import TestCase

from src.models.api.enums import Return
from src.models.api.lookup_wikicitations_qid import LookupWikicitationsQid


class TestLookupWikicitationsQid(TestCase):
    def test_lookup_via_query_service_valid(self):
        lookup = LookupWikicitationsQid()
        result = lookup.lookup_via_query_service(wdqid="Q14452")
        assert result == "Q2680"

    def test_lookup_via_query_service_invalid(self):
        lookup = LookupWikicitationsQid()
        result = lookup.lookup_via_query_service(wdqid="14452")
        assert result == Return.INVALID_QID

    def test_lookup_via_query_service_no_match(self):
        lookup = LookupWikicitationsQid()
        result = lookup.lookup_via_query_service(wdqid="Q14452000000000")
        assert result == Return.NO_MATCH


    def test_lookup_via_cirrussearch(self):
        lookup = LookupWikicitationsQid()
        with self.assertRaises(Exception):
            lookup.lookup_via_cirrussearch(wdqid="Q14452")

