from unittest import TestCase

from src.models.hash_database import HashDatabase


class TestHashDatabase(TestCase):
    def test_connect(self):
        db = HashDatabase()
        db.connect()
        db.initialize()
        # self.fail()

    def test_drop(self):
        db = HashDatabase()
        db.connect()
        db.drop()
        # self.fail()
