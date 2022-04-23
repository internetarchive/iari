import logging
from typing import Optional, Any

import pyssdb
from pydantic import BaseModel, validate_arguments

logger = logging.getLogger(__name__)


class SsdbDatabase(BaseModel):
    password: str = "password"
    port: int = 8888  # "6379"
    host: str = "127.0.0.1"
    connection: Optional[Any]

    def connect(self):
        self.connection = pyssdb.Client(host=self.host, port=self.port)

    def get_info(self):
        return self.connection.info()

    @validate_arguments
    def get_value(self, key: str):
        return self.connection.get(key)

    @validate_arguments
    def set_value(self, key: str, value: str):
        return self.connection.set(key, value)

    @validate_arguments
    def delete(self, key: str):
        return self.connection.delete(key)

    def flush_database(self):
        logger.info("Flushing the SSDB database now")
        return self.connection.flushdb()
