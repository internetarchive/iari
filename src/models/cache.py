import logging
from typing import Optional, Any

from pydantic import BaseModel, validate_arguments

from src import console
from src.models.exceptions import NotLoggedInError
from src.models.ssdb_database import SsdbDatabase
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

logger = logging.getLogger(__name__)


class Cache(BaseModel):
    ssdb: Optional[SsdbDatabase]

    @validate_arguments
    def add_page(self, wikipedia_page: Any, wcdqid: str):
        logger.debug("add_page: Running")
        if self.ssdb is None:
            raise NotLoggedInError()
        if wikipedia_page.md5hash is not None and wcdqid is not None:
            # if type(reference.wikicitations_qid) is not str:
            #     raise ValueError(f"{reference.wikicitations_qid} is not of type str")
            logger.debug(f"Trying to set the value: {wcdqid}")
            return self.ssdb.set_value(key=wikipedia_page.md5hash, value=wcdqid)
        else:
            raise ValueError("did not get what we need")

    @validate_arguments
    def add_reference(self, reference: WikipediaPageReference, wcdqid: str):
        logger.debug("add_reference: Running")
        if self.ssdb is None:
            raise NotLoggedInError()
        if reference.md5hash is not None and wcdqid is not None:
            # if type(reference.wikicitations_qid) is not str:
            #     raise ValueError(f"{reference.wikicitations_qid} is not of type str")
            logger.debug(f"Trying to set the value: {wcdqid}")
            return self.ssdb.set_value(key=reference.md5hash, value=wcdqid)
        else:
            raise ValueError("did not get what we need")

    @validate_arguments
    def add_website(self, reference: WikipediaPageReference, wcdqid: str):
        logger.debug("add_website: Running")
        if self.ssdb is None:
            raise NotLoggedInError()
        if reference.first_level_domain_of_url_hash is not None and wcdqid is not None:
            logger.debug(f"Trying to set the value: {wcdqid}")
            return self.ssdb.set_value(
                key=reference.first_level_domain_of_url_hash, value=wcdqid
            )
        else:
            raise ValueError("did not get what we need")

    # TODO refactor into one generic lookup function?
    @validate_arguments
    def check_page_and_get_wikicitations_qid(
        self,
        wikipedia_page: Any,  # WikipediaPage
    ) -> Optional[str]:
        """We get binary from SSDB so we decode it"""
        if self.ssdb is None:
            raise NotLoggedInError()
        if wikipedia_page.md5hash is not None:
            # https://stackoverflow.com/questions/55365543/
            response = self.ssdb.get_value(key=wikipedia_page.md5hash)
            if response is None:
                return None
            else:
                return str(response.decode("UTF-8"))
        else:
            raise ValueError("md5hash was None")

    @validate_arguments
    def check_reference_and_get_wikicitations_qid(
        self, reference: WikipediaPageReference
    ) -> Optional[str]:
        """We get binary from SSDB so we decode it"""
        if self.ssdb is None:
            raise NotLoggedInError()
        if reference.md5hash is not None:
            # https://stackoverflow.com/questions/55365543/
            response = self.ssdb.get_value(key=reference.md5hash)
            if response is None:
                return None
            else:
                return str(response.decode("UTF-8"))
        else:
            raise ValueError("md5hash was None")

    @validate_arguments
    def check_website_and_get_wikicitations_qid(
        self, reference: WikipediaPageReference
    ) -> Optional[str]:
        """We get binary from SSDB so we decode it"""
        if self.ssdb is None:
            raise NotLoggedInError()
        if reference.first_level_domain_of_url_hash is not None:
            # https://stackoverflow.com/questions/55365543/
            response = self.ssdb.get_value(key=reference.first_level_domain_of_url_hash)
            if response is None:
                return None
            else:
                return str(response.decode("UTF-8"))
        else:
            # Not all references have urls so we fail silently
            return None

    @validate_arguments
    def connect(self, host: str = "127.0.0.1", port: int = 8888):
        # Connect to the SSDB
        self.ssdb = SsdbDatabase(host=host, port=port)
        # try:
        self.ssdb.connect()
        # except:
        #    logger.error("error connection to SSDB")

    @validate_arguments
    def delete_key(self, key: str):
        if self.ssdb is not None:
            return self.ssdb.delete(key=key)
        else:
            raise ValueError("self.ssdb was None")

    def flush_database(self):
        result = self.ssdb.flush_database()
        logger.debug(f"result from SSDB: {result}")
        console.print("Done flushing the SSDB database")

    def get_cache_information(self):
        result = self.ssdb.get_info()
        console.print(result)

    @validate_arguments
    def lookup(self, key: str):
        if self.ssdb:
            return self.ssdb.get_value(key=key)
        else:
            raise ValueError("self.ssdb was None")

    # def get_whole_table(self):
    #     with self.connection.cursor() as cursor:
    #         query = cursor.mogrify(f"SELECT * FROM hashdb.{self.table};")
    #         logger.info(f"running query: {query}")
    #         cursor.execute(query)
    #         return cursor.fetchall()
