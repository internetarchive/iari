import logging
from typing import Any, Optional

# import mariadb
import pymysql
from pydantic import BaseModel, validate_arguments

from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

logger = logging.getLogger(__name__)


class HashDatabase(BaseModel):
    user: str = "root"
    password: str = "password"
    port: int = 3306
    host: str = "localhost"
    connection: Optional[Any]
    table: str = "hashes"

    @validate_arguments
    def add_reference(self, reference: WikipediaPageReference):
        if (reference.md5hash and reference.wikicitations_qid) is not None:
            with self.connection.cursor() as cursor:
                cursor.execute("USE HASHDB")
                query = cursor.mogrify(
                    f"INSERT INTO {self.table} (hash, wikicitations_qid) "
                    f"VALUES ('{reference.md5hash}', '{reference.wikicitations_qid}')"
                )
                cursor.execute(query)
                result = cursor.lastrowid
                self.connection.commit()
                print(f"rowid added:{result}")
        else:
            raise ValueError("did not get what we need")

    @validate_arguments
    def check_reference_and_get_wikicitations_qid(
        self, reference: WikipediaPageReference
    ):
        if reference.md5hash is not None:
            # https://stackoverflow.com/questions/55365543/
            self.connection.ping()
            with self.connection.cursor() as cursor:
                query = cursor.mogrify(
                    f"SELECT hash, wikicitations_qid FROM {self.table} "
                    f"WHERE hash = '{reference.md5hash}';"
                )
                logger.info(f"running query: {query}")
                cursor.execute(query)
                return cursor.fetchone()
        else:
            raise ValueError("md5hash was None")

    def connect(self):
        # Connect to MariaDB Platform
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database="hashdb",
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

    def create_database(self):
        if self.connection is not None:
            with self.connection.cursor() as cursor:
                # create database hashdatabase
                # creating database
                cursor.execute("CREATE DATABASE HASHDB")

    def disconnect(self):
        # Close Connection
        self.connection.close()

    def drop_table_if_exists(self):
        with self.connection.cursor() as cursor:
            cursor.execute(f"drop table if exists {self.table}")

    def initialize(self):
        if self.connection is not None:
            with self.connection.cursor() as cursor:
                # create database hashdatabase
                # creating database
                cursor.execute("USE HASHDB")
                cursor.execute(
                    f"""CREATE TABLE `{self.table}` (
                      `id` int PRIMARY KEY AUTO_INCREMENT,
                      `hash` varchar(32) UNIQUE NOT NULL,
                      `wikicitations_qid` varchar(32) UNIQUE NOT NULL
                    );"""
                )
                cursor.execute(
                    f"CREATE INDEX {self.table}_index ON {self.table}(hash);"
                )

    def get_whole_table(self):
        with self.connection.cursor() as cursor:
            query = cursor.mogrify(f"SELECT * FROM hashdb.{self.table};")
            logger.info(f"running query: {query}")
            cursor.execute(query)
            return cursor.fetchall()
