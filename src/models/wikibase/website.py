import logging

from pydantic import validate_arguments

from src.models.exceptions import MissingInformationError
from src.models.return_.wikibase_return import WikibaseReturn
from src.models.wcd_item import WcdItem
from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference

logger = logging.getLogger(__name__)


class Website(WcdItem):
    """This models a Website item in Wikicitations

    It holds the return from the cache"""

    reference: WikipediaReference

    @validate_arguments
    def __insert_website_in_cache__(self, wcdqid: str, testing: bool = False):
        logger.debug("__insert_website_in_cache__: Running")
        if testing and not self.cache:
            self.__setup_cache__()
        if not self.cache:
            raise ValueError("self.cache was None")
        else:
            self.cache.add_website(reference=self.reference, wcdqid=wcdqid)
        logger.info("Reference inserted into the hash database")

    @validate_arguments
    def __upload_website_to_wikibase__(
        self, wikipedia_article: WcdItem
    ) -> WikibaseReturn:
        """This is a lower level method that only handles uploading the website item"""
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        if not isinstance(wikipedia_article, WikipediaArticle):
            raise TypeError("not a WikipediaArticle")
        if not wikipedia_article.wikibase:
            raise MissingInformationError("wikipedia_article.wikibase was None")
        self.wikibase = wikipedia_article.wikibase
        if self.wikibase_crud_create is None:
            self.__setup_wikibase_crud_create__()
        if self.wikibase_crud_create is not None:
            return_ = self.wikibase_crud_create.prepare_and_upload_website_item(
                page_reference=self.reference, wikipedia_article=wikipedia_article
            )
            if isinstance(return_, WikibaseReturn):
                return return_
            else:
                raise ValueError(f"we did not get a WikibaseReturn back")
        else:
            raise ValueError("self.wikicitations was None")

    @validate_arguments
    def check_and_upload_website_item_to_wikibase_if_missing(
        self, wikipedia_article: WcdItem
    ):
        """This method checks if a website item is present
        using the first_level_domain_of_url_hash and the cache if
        enabled and uploads a new item if not"""
        logger.debug("check_and_upload_website_item_to_wikibase_if_missing: Running")
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        if not isinstance(wikipedia_article, WikipediaArticle):
            raise TypeError("not a WikipediaArticle")
        if self.reference is None:
            raise ValueError("reference was None")
        if self.reference.first_level_domain_of_url_hash is None:
            raise ValueError("reference.first_level_domain_of_url_hash was None")
        logger.debug("Checking and uploading website item")
        self.get_website_wcdqid_from_cache()
        if self.return_ and self.return_.item_qid:
            logger.debug(f"Got wcdqid:{self.return_.item_qid} from the cache")
            self.reference.website_item = self
            logger.info(f"Added link to existing website item {self.return_.item_qid}")
        else:
            self.__upload_website_and_insert_in_the_cache__(
                wikipedia_article=wikipedia_article
            )
        return self.reference

    @validate_arguments
    def get_website_wcdqid_from_cache(self) -> None:
        if not self.cache:
            raise ValueError("self.cache was None")
        if self.cache:
            self.return_ = self.cache.check_website_and_get_wikibase_qid(
                reference=self.reference
            )
            if self.return_:
                logger.debug(f"result from the cache:{self.return_.item_qid}")

    @validate_arguments
    def __upload_website_and_insert_in_the_cache__(
        self, wikipedia_article: WcdItem, testing: bool = False
    ) -> None:
        if testing and not self.cache:
            self.__setup_cache__()
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        if not isinstance(wikipedia_article, WikipediaArticle):
            raise TypeError("not a WikipediaArticle")
        self.return_ = self.__upload_website_to_wikibase__(
            wikipedia_article=wikipedia_article
        )
        wcdqid = self.return_.item_qid
        if wcdqid is None:
            raise ValueError("WCDQID was None")
        if self.reference.first_level_domain_of_url_hash is None:
            raise ValueError("first_level_domain_of_url_hash was None")
        logger.debug(
            f"Hash before insertion: {self.reference.first_level_domain_of_url_hash}. "
            f"WCDQID before insertion: {wcdqid}"
        )
        self.__insert_website_in_cache__(
            wcdqid=wcdqid,
        )
        self.reference.website_item = self
        logger.info(f"Added website item {wcdqid} to WCD")
