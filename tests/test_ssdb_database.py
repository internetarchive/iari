from unittest import TestCase

from src.models.ssdb_database import SsdbDatabase


class TestSsdbDatabase(TestCase):
    @staticmethod
    def test_set():
        r = SsdbDatabase()
        r.connect()
        r.set_value(key="test", value="test")
        result = r.get_value("test").decode("UTF-8")
        print(result)
        assert result == "test"

    def test_flush_database(self):
        r = SsdbDatabase()
        r.connect()
        r.set_value(key="test", value="test")
        r.flush_database()
        result = r.get_value("test")
        # print(result)
        assert result is None
