from typing import Optional, Any

import redis
from pydantic import BaseModel


class RedisDatabase(BaseModel):
    password: str = "password"
    port: int = 6379
    host: str = "localhost"
    connection: Optional[Any]
    table: str = "hashes"

    def connect(self):
        connection = redis.Redis(host=self.host, port=self.port, password=self.password)

    def set(self):
        self.connection.set("foo", "bar")
        value = self.connection.get("foo")
        print(value)

    def get(self):
        return self.connection.get("foo")
