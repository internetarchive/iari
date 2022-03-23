import logging
import sys
from typing import Any, Optional

from pydantic import BaseModel, validate_arguments

# import mariadb
import pymysql
from pymysql import OperationalError

from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

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
            self.cursor.execute("USE HASHDB")
            self.cursor.execute(
                """CREATE TABLE `hashes` (
                  `id` int PRIMARY KEY AUTO_INCREMENT,
                  `hash` varchar(32) UNIQUE NOT NULL,
                  `wikicitations_qid` varchar(32) UNIQUE NOT NULL
                );"""
            )
            self.cursor.execute("CREATE INDEX hash_index ON hashes(hash);")

    def drop_if_exists(self):
        try:
            self.cursor.execute("DROP DATABASE HASHDB")
        except OperationalError:
            logger.error("Skipping drop. No database 'hashdb' found")

    def disconnect(self):
        # Close Connection
        self.connection.close()

    @validate_arguments
    def check_reference_and_get_wikicitations_qid(
        self, reference: WikipediaPageReference
    ):
        if reference.md5hash is not None:
            self.cursor.execute(
                f"SELECT hash, wikicitations_qid FROM hashes WHERE hash = '{reference.md5hash}'"
            )
            return self.cursor.fetchone()
        else:
            raise ValueError("md5hash was None")

    @validate_arguments
    def add_reference(self, reference: WikipediaPageReference):
        if (reference.md5hash and reference.wikicitations_qid) is not None:
            self.cursor.execute(
                f"INSERT INTO hashes (hash, wikicitations_qid) "
                f"VALUES ('{reference.md5hash}', '{reference.wikicitations_qid}')"
            )
            result = self.cursor.fetchone()
            print(f"add:{result}")
        else:
            raise ValueError("did not get what we need")
