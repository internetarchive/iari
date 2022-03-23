import logging
import sys
from typing import Any, Optional

from pydantic import BaseModel

# import mariadb
import pymysql

logger = logging.getLogger(__name__)


class HashDatabase(BaseModel):
    user: str = "root"
    password: str = "password"
    port: int = 3306
    host: str = "localhost"
    cursor: Optional[Any]
    connection: Optional[Any]

    def connect(self):
        # Connect to MariaDB Platform
        try:
            self.connection = pymysql.connect(
                host=self.host, user=self.user, password=self.password, port=self.port
            )
            # self.connection = mariadb.connect(
            #     user=self.user,
            #     password=self.password,
            #     host=self.host,
            #     port=self.port,
            #     # database="employees",
            # )
        # except mariadb.Error as e:
        #     print(f"Error connecting to MariaDB Platform: {e}")
        #     sys.exit(1)
        except:
            logger.error("error")
        # Get Cursor
        self.cursor = self.connection.cursor()

    def initialize(self):
        if self.cursor is not None:
            # create db hashdatabase
            # creating database
            self.cursor.execute("CREATE DATABASE HASHDB")

    def drop(self):
        self.cursor.execute("DROP DATABASE HASHDB")

    def disconnect(self):
        # Close Connection
        self.connection.close()
