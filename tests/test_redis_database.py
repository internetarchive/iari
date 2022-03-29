from unittest import TestCase

from src.models.redis_database import RedisDatabase


class TestRedisDatabase(TestCase):
    def test_set(self):
        r = RedisDatabase()
        r.connect()
        r.set("test", "test")
        result = r.get("test").decode("UTF-8")
        print(result)
        assert result == "test"
        # self.fail()
