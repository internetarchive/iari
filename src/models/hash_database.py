import logging
from typing import Any, Optional

# import mariadb
import pymysql
from pydantic import BaseModel, validate_arguments

from src.models.ssdb_database import SsdbDatabase
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

logger = logging.getLogger(__name__)


class HashDatabase(BaseModel):
    ssdb: SsdbDatabase

    @validate_arguments
    def add_reference(self, reference: WikipediaPageReference):
        if (reference.md5hash and reference.wikicitations_qid) is not None:
            return self.ssdb.set(
                key=reference.md5hash, value=reference.wikicitations_qid
            )
        else:
            raise ValueError("did not get what we need")

    @validate_arguments
    def check_reference_and_get_wikicitations_qid(
        self, reference: WikipediaPageReference
    ):
        if reference.md5hash is not None:
            # https://stackoverflow.com/questions/55365543/
            return self.ssdb.get(key=reference.md5hash)
        else:
            raise ValueError("md5hash was None")

    def connect(self):
        # Connect to MariaDB Platform
        self.ssdb = SsdbDatabase()
        try:
            self.ssdb.connect()
        except:
            logger.error("error")

    # def get_whole_table(self):
    #     with self.connection.cursor() as cursor:
    #         query = cursor.mogrify(f"SELECT * FROM hashdb.{self.table};")
    #         logger.info(f"running query: {query}")
    #         cursor.execute(query)
    #         return cursor.fetchall()
