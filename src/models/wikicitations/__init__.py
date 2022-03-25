import logging
from datetime import datetime, timezone
from typing import Any, Optional, List

from pydantic import BaseModel, validate_arguments
from wikibaseintegrator import wbi_config, datatypes
from wikibaseintegrator.entities import ItemEntity
from wikibaseintegrator.models import Claim

import config
from src.models.wikicitations.enums import Property
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

logger = logging.getLogger(__name__)


class WikiCitations(BaseModel):
    """This class models the WikiCitations Wikibase and handles all uploading to it

    We want to create items for all Wikipedia pages and references with a unique hash"""

    @validate_arguments
    def __prepare_new_wikipedia_page_item__(
        self, wikipedia_page: WikipediaPage
    ) -> ItemEntity:
        """This method converts a reference into a new WikiCitations item"""
        wbi = WikibaseIntegrator(
            login=wbi_login.Login(user=config.user, password=config.pwd),
        )
        item = wbi.item.new()
        item.labels.set("en", wikipedia_page.pywikibot_page.title)
        item.descriptions.set(
            "en", f"page from {wikipedia_page.wikimedia_site.name.title()}"
        )
        # Prepare claims
        # First prepare the reference needed in other claims
        citations = self.__prepare_citations__()
        if len(citations) > 0:
            item.add_claims()
        item.add_claims(
            self.__prepare_single_value_wikipedia_page_claims__(
                wikipedia_page=wikipedia_page
            ),
        )
        if config.loglevel == logging.DEBUG:
            logger.debug("Printing the item json")
            print(item.get_json())
            exit()
        return item

    @validate_arguments
    def __prepare_new_reference_item__(
        self, page_reference: WikipediaPageReference, wikipedia_page: WikipediaPage
    ) -> ItemEntity:
        """This method converts a reference into a new WikiCitations item"""
        wbi = WikibaseIntegrator(
            login=wbi_login.Login(user=config.user, password=config.pwd),
        )
        item = wbi.item.new()
        item.labels.set("en", page_reference.title)
        item.descriptions.set(
            "en", f"reference from {wikipedia_page.wikimedia_site.name.title()}"
        )
        # Prepare claims
        # First prepare the reference needed in other claims
        item.add_claims(
            self.__prepare_single_value_reference_claims__(
                page_reference=page_reference
            ),
        )
        if config.loglevel == logging.DEBUG:
            logger.debug("Printing the item json")
            print(item.get_json())
            exit()
        return item

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

    def __prepare_single_value_reference_claims__(
        self, page_reference: WikipediaPageReference
    ):
        logger.info("Preparing single value claims")
        doi = None
        pmid = None
        orcid = None
        isbn_10 = None
        isbn_13 = None
        if page_reference.doi is not None:
            doi = datatypes.ExternalID(
                prop_nr=Property.DOI.value,
                value=page_reference.doi,
            )
        if page_reference.orcid is not None:
            orcid = datatypes.ExternalID(
                prop_nr=Property.ORCID.value,
                value=page_reference.orcid,
            )
        if page_reference.pmid is not None:
            pmid = datatypes.ExternalID(
                prop_nr=Property.PMID.value,
                value=page_reference.pmid,
            )
        if page_reference.isbn_10 is not None:
            isbn_10 = datatypes.ExternalID(
                prop_nr=Property.ISBN_10.value,
                value=page_reference.isbn_10,
            )
        if page_reference.isbn_13 is not None:
            isbn_13 = datatypes.ExternalID(
                prop_nr=Property.ISBN_13.value,
                value=page_reference.isbn_13,
            )
        # TODO gather the statements

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
        # doi
        # isbn-13 and isbn-10
        #
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
