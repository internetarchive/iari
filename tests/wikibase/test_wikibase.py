from unittest import TestCase

from src.models.wikibase.wikicitations_wikibase import WikiCitationsWikibase


class TestWikibase(TestCase):
    def test_valid_qid_invalid_input(self):
        """We instantiate WikiCitationsWikibase here but the methods are inherited from Wikibase"""
        wcw = WikiCitationsWikibase()
        assert wcw.is_valid_qid(qid="123") is False

    def test_valid_qid_valid_input(self):
        """We instantiate WikiCitationsWikibase here but the methods are inherited from Wikibase"""
        wcw = WikiCitationsWikibase()
        assert wcw.is_valid_qid(qid="Q123") is True

    def test_valid_qid_valid_input_lowercase(self):
        """We instantiate WikiCitationsWikibase here but the methods are inherited from Wikibase"""
        wcw = WikiCitationsWikibase()
        assert wcw.is_valid_qid(qid="q123") is True

    def test_valid_qid_invalid_input_alpha(self):
        """We instantiate WikiCitationsWikibase here but the methods are inherited from Wikibase"""
        wcw = WikiCitationsWikibase()
        assert wcw.is_valid_qid(qid="q123a") is False
