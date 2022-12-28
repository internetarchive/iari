from unittest import TestCase

from src import MissingInformationError
from src.models.hashing import Hashing


class TestHashing(TestCase):
    def test___entity_updated_hash__(self):
        h = Hashing()
        h.article_wikidata_qid = "Q1"
        # print(m.__entity_updated_hash__())
        assert (
            "6571bcc708dbebba0616aaabd3d0e98a"
            == h.__generate_entity_updated_hash_key__()
        )
        h.article_wikidata_qid = ""
        h.title = "Q1"
        # print(m.__entity_updated_hash__())
        assert (
            "6571bcc708dbebba0616aaabd3d0e98a"
            == h.__generate_entity_updated_hash_key__()
        )
        h.title = h.article_wikidata_qid = ""
        with self.assertRaises(MissingInformationError):
            h.__generate_entity_updated_hash_key__()

    def test_generate_raw_reference_hash(self):
        h = Hashing(raw_template="test")
        hash_ = h.generate_raw_reference_hash()
        assert hash_ == "098f6bcd4621d373cade4e832627b4f6"
        h.raw_template = ""
        with self.assertRaises(MissingInformationError):
            h.generate_raw_reference_hash()
