from __future__ import annotations

import logging
from typing import Any, Optional

from wikibaseintegrator import WikibaseIntegrator, wbi_login  # type: ignore
from wikibaseintegrator.datatypes import BaseDataType  # type: ignore
from wikibaseintegrator.entities import ItemEntity  # type: ignore
from wikibaseintegrator.models import Claim, Claims  # type: ignore
from wikibaseintegrator.wbi_enums import ActionIfExists  # type: ignore
from wikibaseintegrator.wbi_exceptions import ModificationFailed  # type: ignore

import config
from src import console
from src.models.exceptions import MissingInformationError
from src.models.wcd_item import WcdItem
from src.models.wikibase.crud import WikibaseCrud
from src.models.wikibase.crud.read import WikibaseCrudRead
from src.models.wikibase.enums import WriteRequired
from src.models.wikimedia.wikipedia.references.wikipedia import WikipediaReference
from src.models.wikimedia.wikipedia.wikipedia_article import WikipediaArticle

logger = logging.getLogger(__name__)


class WikibaseCrudUpdate(WikibaseCrud):
    """This class handles all comparing and updating of Wikibase items

    entity: is the entity to compare. Either a WikipediaPage or a WikipediaReference
    new_item: new item based on fresh data from Wikipedia
    wikibase_item: current item in the Wikibase
    wikipedia_article: is the page the reference belongs to"""

    entity: Optional[WcdItem] = None
    new_item: Optional[ItemEntity] = None
    testing: bool = False
    existing_wikibase_item: Optional[ItemEntity] = None
    wikipedia_article: Optional[Any] = None

    class Config:
        arbitrary_types_allowed = True

    # @property
    # def write_required(self):
    #     """This property method determines whether write is required for self.wikibase_item"""
    #     logger.debug("write_required: running")
    #     base_filter = []
    #     properties = Properties()
    #     property_names = properties.get_all_property_names()
    #     for name in property_names:
    #         base_filter.append(BaseDataType(prop_nr=getattr(self.wikibase, name)))
    #     if config.loglevel == logging.DEBUG:
    #         logger.debug("Basefilter:")
    #         console.print(base_filter)
    #     return self.existing_wikibase_item.write_required(base_filter=base_filter)

    def __compare_claims_and_upload__(
        self,
    ) -> WriteRequired:
        """We compare claims one by one and update the item in the end

        The algorithm for comparing is the __eq__ method in WBI which compares 3 qualities:
        1) property number
        2) datavalue
        3) qualifiers

        This comparison will never find/correct statements that refer to a deleted item.
        To fix those we need another approach.

        If we know which properties can have multiple values, then we can detect when
        a claim is outdated in all other properties like WEBSITE, etc."""
        if not self.new_item:
            raise MissingInformationError("self.new_item was None")
        if not self.existing_wikibase_item:
            raise MissingInformationError("self.wikibase_item was None")
        with console.status("Comparing claims and uploading the result to Wikibase..."):
            from src.models.wikimedia.wikipedia.wikipedia_article import (
                WikipediaArticle,
            )

            updated_claims = self.existing_wikibase_item.claims
            if isinstance(self.entity, WikipediaArticle):
                multiple_values_properties = [
                    self.wikibase.CITATIONS,
                    self.wikibase.STRING_CITATIONS,
                ]
                # First remove all old claims no longer present
                for claim in updated_claims:
                    # This comparison only looks at property number and datavalue
                    if (
                        claim not in self.new_item.claims
                        and claim.mainsnak.property_number in multiple_values_properties
                    ):
                        logger.debug(
                            f"Removing claim with property {claim.mainsnak.property_number} "
                            f"and value {claim.mainsnak.datavalue} which is not "
                            f"present in the page item anymore"
                        )
                        claim.remove()
                        # raise DebugExit()
                # Add new claims
                for new_claim in self.new_item.claims:
                    new_property_id = new_claim.mainsnak.property_number
                    # TODO fetch property_label to enable a better UI
                    if new_property_id not in multiple_values_properties:
                        # Replace all claims for properties which we don't want to keep multiple values for
                        # logger.debug(
                        #     f"Replacing claim on single-value property {new_claim}"
                        # )
                        updated_claims.add(claims=new_claim)
                    else:
                        # The property in question is a multi-value property so we append/replace
                        # logger.debug(
                        #     f"Appending or replacing claim on multi-value property {new_claim}"
                        # )
                        updated_claims.add(
                            claims=new_claim,
                            action_if_exists=ActionIfExists.APPEND_OR_REPLACE,
                        )
            elif isinstance(self.entity, WikipediaReference):
                logger.debug("Going through reference claims")
                # There currently are no multi-value properties in use on references
                # so we simply replace them all
                if config.compare_references:
                    updated_claims.add(
                        claims=self.new_item.claims,
                        action_if_exists=ActionIfExists.REPLACE_ALL,
                    )
                else:
                    updated_claims.add(
                        claims=self.new_item.claims,
                        action_if_exists=ActionIfExists.APPEND_OR_REPLACE,
                    )
                # debug check to see if we only have one website value left on P81
                website_claims = [
                    claim
                    for claim in updated_claims
                    if claim.mainsnak.property_number == self.wikibase.WEBSITE
                    and claim.removed is False
                ]
                if len(website_claims) > 1:
                    console.print(website_claims)
                    raise Exception(
                        "More than one website claim present "
                        "in the generated item, this is a bug."
                    )
            else:
                raise ValueError("Not a supported entity type")
            # Update the item with the updated claims
            self.existing_wikibase_item.claims = updated_claims
            # self.__print_claim_statistics__()
            # if self.write_required:
            if not self.testing:
                self.__setup_wikibase_integrator_configuration__()
                try:
                    self.existing_wikibase_item.write(
                        summary=f"Updated the item based on changes in Wikipedia"
                    )
                    console.print(
                        f"Updated the item based on changes in Wikipedia, "
                        f"see {self.wikibase.entity_history_url(item_id=self.existing_wikibase_item.id)}"
                    )
                    return WriteRequired.YES
                except ModificationFailed as e:
                    message = (
                        f"The {self.entity.__repr__()} item {self.existing_wikibase_item.id} "
                        f"could not be updated because of this error: {e}"
                    )
                    logger.error(message)
                    self.__log_to_file__(message=message, file_name="update-failed.log")
                    # raise DebugExit()
                    return WriteRequired.YES
            else:
                return WriteRequired.NO
            # else:
            #         console.print(
            #             "Write required but skipping because of testing was True"
            #         )
            #         return WriteRequired.YES
            # else:
            #     console.print("No write required according to WikibaseIntegrator")
            #     return WriteRequired.NO

    # def __print_claim_statistics__(self):
    #     """We print the statistics of all the claims"""
    #     pass
    #     # current_property_numbers = {
    #     #     claim.mainsnak.property_number for claim in wikibase_item.claims
    #     # }
    #     # logger.info(
    #     #     f"Found these property numbers {current_property_numbers} in the item in Wikibase"
    #     # )
    #     # new_property_numbers = {
    #     #     claim.mainsnak.property_number for claim in new_item.claims
    #     # }
    #     # logger.info(
    #     #     f"Found these property numbers {new_property_numbers} on the newly prepared item"
    #     # )

    def compare_and_update_claims(self, entity: WcdItem) -> WriteRequired:
        """We compare and update claims that are completely missing from the Wikibase item.
        We also remove reference claims no longer present in the Wikipedia page."""
        logger.debug("compare_and_update_claims: Running")
        if not isinstance(entity, WcdItem):
            raise TypeError("entity was not a WcdItem instance")
        self.entity = entity
        if not self.wikipedia_article:
            raise MissingInformationError("self.wikipedia_article was None")
        if not entity.return_:
            raise MissingInformationError("new_reference.return_ was None")
        if entity.return_.uploaded_now:
            logger.info("Skipping comparison because the reference was just uploaded")
            return WriteRequired.NO
        else:
            self.__fetch_and_prepare_data_for_comparison__()
            return self.__compare_claims_and_upload__()

    def __fetch_and_prepare_data_for_comparison__(self):
        """Fetch and prepare the information needed to perform a comparison"""
        logger.debug("__fetch_and_prepare_data_for_comparison__: Running")
        wcr = WikibaseCrudRead(wikibase=self.wikibase)
        if isinstance(self.entity, WikipediaReference):
            if self.entity.title:
                console.print(
                    f"Comparing {self.entity.template_name} "
                    f"reference with the title '{self.entity.title}'"
                )
            else:
                console.print(
                    f"Comparing {self.entity.template_name} "
                    f"reference with missing title"
                )
            logger.info(
                f"See {self.wikibase.entity_url(item_id=self.entity.return_.item_qid)}"
            )
            self.new_item = wcr.__prepare_new_reference_item__(
                page_reference=self.entity, wikipedia_article=self.wikipedia_article
            )
        else:
            if isinstance(self.entity, WikipediaArticle) and self.entity.title:
                logger.info(f"Comparing page with title '{self.entity.title}")
                self.new_item = wcr.__prepare_new_wikipedia_article_item__(
                    wikipedia_article=self.entity
                )
            else:
                raise MissingInformationError("entity or entity.title was None")
        if not self.testing:
            # We always overwrite the item if not testing
            self.existing_wikibase_item = wcr.get_item(
                item_id=self.entity.return_.item_qid
            )
            if not self.existing_wikibase_item:
                raise ValueError(
                    "Cannot compare because the "
                    "item was not found in the Wikibase. "
                    "This should never happen."
                )
        else:
            if not self.existing_wikibase_item:
                raise ValueError(
                    "Cannot compare because the " "wikibase_item was not set"
                )
