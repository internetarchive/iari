import logging
from datetime import datetime, timezone
from typing import Any, Optional, List

from pydantic import BaseModel, validate_arguments
from wikibaseintegrator import wbi_config, datatypes
from wikibaseintegrator.entities import ItemEntity
from wikibaseintegrator.models import Claim

import config
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

logger = logging.getLogger(__name__)


class WikiCitations(BaseModel):
    """This class models the WikiCitations Wikibase and handles all uploading to it

    We want to create items for all Wikipedia pages and references with a unique hash"""

    wikipedia_page: Any
    wikicitations_qid: Optional[str]

    @staticmethod
    def __prepare_reference_claim__() -> List[Claim]:
        logger.info("Preparing reference claim")
        # Prepare reference
        retrieved_date = datatypes.Time(
            prop_nr="P813",  # Fetched today
            time=datetime.utcnow()
            .replace(tzinfo=timezone.utc)
            .replace(
                hour=0,
                minute=0,
                second=0,
            )
            .strftime("+%Y-%m-%dT%H:%M:%SZ"),
        )
        claims = []
        for claim in (retrieved_date, openalex_id):
            if claim is not None:
                claims.append(claim)
        return claims

    def __prepare_single_value_claims__(self):
        if (work, doi, reference) is None:
            raise ValueError("did not get what we need")
        logger.info("Preparing other claims")
        doi = datatypes.ExternalID(
            prop_nr=Property.DOI.value,
            value=doi.lower(),  # This is a community norm in Wikidata
            references=[reference],
        )

    def __upload_new_item__(self, item: ItemEntity):
        if item is None:
            raise ValueError("Did not get what we need")
        if config.upload_enabled:
            new_item = item.write(summary="New item imported from Wikipedia")
            print(f"Added new item {self.entity_url(new_item.id)}")
            if config.press_enter_to_continue:
                input("press enter to continue")
        else:
            print("skipped upload")

    @validate_arguments
    def prepare_and_upload_reference_item(
        self, page_reference: WikipediaPageReference
    ) -> str:
        # pseudo
        # prepare the statements
        # upload
        raise NotImplementedError()

    @validate_arguments
    def prepare_and_upload_wikipedia_page_item(self, wikipedia_page: Any) -> str:
        from src import WikipediaPage

        if not isinstance(wikipedia_page, WikipediaPage):
            raise ValueError("did not get a WikipediaPage object")
        # pseudo code
        # prepare statements for all references
        # prepare the rest of the statements
        # upload
        raise NotImplementedError()

    @staticmethod
    def entity_url(qid):
        return f"{wbi_config.config['WIKIBASE_URL']}/wiki/{qid}"
