import logging

from pydantic import validate_arguments
from wikibaseintegrator import WikibaseIntegrator, datatypes, wbi_login  # type: ignore
from wikibaseintegrator.entities import ItemEntity  # type: ignore
from wikibaseintegrator.models import (  # type: ignore
    Claim,
    Qualifiers,
    Reference,
    References,
)
from wikibaseintegrator.wbi_exceptions import ModificationFailed  # type: ignore

import config
from src.helpers import console
from src.models.exceptions import MissingInformationError
from src.models.wikibase.crud import WikibaseCrud
from src.models.wikibase.wikibase_return import WikibaseReturn

logger = logging.getLogger(__name__)


class WikibaseCrudCreate(WikibaseCrud):
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __upload_new_item__(self, item: ItemEntity) -> str:
        """Upload the new item to WikiCitations"""
        if item is None:
            raise ValueError("Did not get what we need")
        if config.loglevel == logging.DEBUG:
            logger.debug("Finished item JSON")
            console.print(item.get_json())
        try:
            new_item = item.write(summary="New item imported from Wikipedia")
            print(f"Added new item {self.entity_url(new_item.id)}")
            if config.press_enter_to_continue:
                input("press enter to continue")
            logger.debug(f"returning new wcdqid: {new_item.id}")
            return str(new_item.id)
        except ModificationFailed as modification_failed:
            """Catch, extract and return the conflicting WCDQID"""
            logger.info(modification_failed)
            wcdqid = modification_failed.get_conflicting_entity_id
            if wcdqid is None:
                raise MissingInformationError("wcdqid was None")
            return str(wcdqid)
