from typing import Optional, Any

import redis
from pydantic import BaseModel, validate_arguments


class SsdbDatabase(BaseModel):
    password: str = "password"
    port: int = "8888"  # "6379"
    host: str = "127.0.0.1"
    connection: Optional[Any]

    def connect(self):
        self.connection = redis.Redis(host=self.host, port=self.port)

    @validate_arguments
    def set(self, key: str, value: str):
        return self.connection.set(key, value)

    @validate_arguments
    def get(self, key: str):
        return self.connection.get(key)
