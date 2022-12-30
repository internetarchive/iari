from unittest import TestCase

from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer


class TestWikipediaAnalyzer(TestCase):
    def test_print_statistics(self):
        wa = WikipediaAnalyzer(title="Easter Island")
        wa.print_statistics()
    def test__gather_statistics__(self):
        pass
    def test__analyze__(self):
        pass