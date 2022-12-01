import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import config
from src.models.cache import Cache
from src.models.exceptions import MissingInformationError
from src.models.hashing import Hashing
from src.wcd_base_model import WcdBaseModel

logger = logging.getLogger(__name__)


class UpdateDelay(WcdBaseModel):
    """This class accepts a message or reference and
    helps determine if the update delay has passed or not"""

    cache: Optional[Cache] = None
    object_: Any
    time_of_last_update: Optional[datetime]

    def time_to_update(self, testing: bool = False) -> bool:
        self.time_of_last_update = self.__convert_to_datetime__(
            timestamp=self.__get_timestamp_from_cache__(testing=testing)
        )
        return self.__delay_time_has_passed__()

    def __delay_time_has_passed__(self) -> bool:
        """We return true if the delay has passed and False otherwise"""
        logger.debug("__delay_time_has_passed__: running")
        if self.time_of_last_update:
            from src.models.message import Message
            from src.models.wikimedia.wikipedia.article import WikipediaArticle
            from src.models.wikimedia.wikipedia.reference.generic import (
                WikipediaReference,
            )

            # TODO change from hours to minutes
            if isinstance(self.object_, Message) or isinstance(
                self.object_, WikipediaArticle
            ):
                logger.info("Using delay time for article")
                result = self.time_of_last_update < (
                    datetime.now()
                    - timedelta(hours=config.article_update_delay_in_hours)
                )
            elif isinstance(self.object_, WikipediaReference):
                logger.info("Using delay time for reference")
                result = self.time_of_last_update < (
                    datetime.now()
                    - timedelta(hours=config.reference_update_delay_in_hours)
                )
            else:
                raise ValueError("could not recognize self.object_")
            logger.info(f"Delay time has passed: {result}")
            return result
        else:
            raise ValueError("self.time_of_last_update was None")

    def __get_entity_updated_hash_key__(self) -> str:
        from src.models.message import Message

        if isinstance(self.object_, Message):
            hashing = Hashing(
                wikibase=self.object_.wikibase,
                language_code=self.object_.language_code,
                article_wikidata_qid=self.object_.article_wikidata_qid,
                title=self.object_.title,
                wikimedia_site=self.object_.wikimedia_site,
            )
        else:
            from src.models.wikimedia.wikipedia.article import WikipediaArticle
            from src.models.wikimedia.wikipedia.reference.generic import (
                WikipediaReference,
            )

            if not isinstance(self.object_, WikipediaReference) and not isinstance(
                self.object_, WikipediaArticle
            ):
                raise ValueError(
                    "did not get Message or WikipediaReference or WikipediaArticle"
                )
            hashing = Hashing(
                wikibase=self.object_.wikibase,
                language_code=self.object_.language_code,
                title=self.object_.title,
                wikimedia_site=self.object_.wikimedia_site,
            )
        return hashing.__generate_entity_updated_hash_key__()

    def __get_timestamp_from_cache__(self, testing: bool = False):
        if testing and not self.cache:
            self.__setup_cache__()
        if not self.cache:
            raise ValueError("self.cache was None")
        if not self.object_:
            raise MissingInformationError("self.object_ was None")
        timestamp_string = self.cache.lookup_title_or_wdqid_last_updated(
            key=self.__get_entity_updated_hash_key__()
        )
        return float(timestamp_string)

    def __convert_to_datetime__(self, timestamp: float = 0.0) -> datetime:
        if not timestamp:
            raise MissingInformationError("timestamp was 0.0")
        else:
            return datetime.fromtimestamp(timestamp)
