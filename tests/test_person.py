from unittest import TestCase

from src.models.person import Person


class TestPerson(TestCase):
    def test_full_name(self):
        p = Person(given="test", surname="test")
        assert p.full_name == "test test"
        p2 = Person(name_string="testtest")
        assert p2.full_name == "testtest"
        p3 = Person(name_string="")
        assert p3.full_name == ""

    def test_has_number(self):
        p = Person(given="test", surname="test")
        assert p.has_number is False
        p = Person(given="test", surname="test", number_in_sequence=1)
        assert p.has_number is True
