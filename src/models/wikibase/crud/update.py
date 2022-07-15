from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, List, Optional, Union

from pydantic import validate_arguments
from wikibaseintegrator import WikibaseIntegrator, wbi_login  # type: ignore
from wikibaseintegrator.entities import ItemEntity  # type: ignore
from wikibaseintegrator.models import Claim  # type: ignore
from wikibaseintegrator.wbi_enums import ActionIfExists  # type: ignore
from wikibaseintegrator.wbi_exceptions import ModificationFailed  # type: ignore

from src import console
from src.models.exceptions import MissingInformationError
from src.models.wikibase.crud import WikibaseCrud
from src.models.wikibase.crud.read import WikibaseCrudRead
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

if TYPE_CHECKING:
    from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

logger = logging.getLogger(__name__)


class WikibaseCrudUpdate(WikibaseCrud):
    class Config:
        arbitrary_types_allowed = True

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __compare_claims_and_upload__(
        self,
        entity: Any,  # Union["WikipediaPage", WikipediaPageReference],
        new_item: ItemEntity,
        wikibase_item: ItemEntity,
        testing: bool = False,
    ) -> List[Claim]:
        """We compare claims one by one and update the item in the end"""
        with console.status("Updating claims and uploading to Wikibase..."):
            from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

            if isinstance(entity, WikipediaPage):
                # We remove these because we want to update them easily
                # Another and harder way is to compare all values and
                # deprecate the ones that are now gone.
                # This collides with the following user story:
                # "as a user I want to know if a reference has disappeared from the page and when"
                logger.debug("__compare_claims__: deleting all reference claims")
                wikibase_item.claims.remove(property=self.wikibase.CITATIONS)
                wikibase_item.claims.remove(property=self.wikibase.STRING_CITATIONS)
            claims_to_be_added = []
            property_numbers = {
                claim.mainsnak.property_number for claim in wikibase_item.claims
            }
            logger.debug(f"Found these property numbers {property_numbers}")
            for claim in new_item.claims:
                # For now we only update statements that are completely missing
                # We thus do not add/remove qualifiers or references
                # nor update any values on existing statements
                if claim.mainsnak.property_number not in property_numbers:
                    # For now we don't update the hash even though adding
                    # oclc, pmid, doi, isbn cause the hash to change
                    logger.debug(f"Adding missing claim {claim}")
                    wikibase_item.claims.add(
                        claim, action_if_exists=ActionIfExists.KEEP
                    )
                    claims_to_be_added.append(claim)
            number_of_added_claims = len(claims_to_be_added)
            if number_of_added_claims > 0:
                if not testing:
                    self.__setup_wikibase_integrator_configuration__()
                    try:
                        wikibase_item.write(
                            summary=(
                                f"Updated the item with {number_of_added_claims} more claims "
                                "based on changes in Wikipedia"
                            )
                        )
                        console.print(
                            f"Added {number_of_added_claims} new claims to this item"
                        )
                        return claims_to_be_added
                    except ModificationFailed as e:
                        message = f"The {entity.__repr_name__()} item {wikibase_item.id} could not be updated because of this error: {e}"
                        logger.error(message)
                        self.__log_to_file__(
                            message=message, file_name="update-failed.log"
                        )
                        return []
                else:
                    logger.info(
                        f"Found {number_of_added_claims} claims to be added to this item"
                    )
                    return claims_to_be_added
            elif len(wikibase_item.claims) != len(new_item.claims):
                if not testing:
                    self.__setup_wikibase_integrator_configuration__()
                    wikibase_item.write(
                        summary=(
                            "Removed claims "
                            "based on changes in Wikipedia"
                            "This is an edge case and should rarely happen. "
                            "Example: a page had one reference and it was "
                            "removed since last update"
                        )
                    )
                    console.print(
                        f"Updated the item with fewer claims than before. "
                        f"This is an edge case and should rarely happen. "
                        f"Example: a page had one reference and it was "
                        f"removed since last update"
                    )
                    return []
                else:
                    logger.info(
                        "Claims were removed. "
                        "But updating was skipped because testing was True."
                    )
                    return []
            else:
                console.print(
                    f"No new claims were added so we skip updating."  # this {entity.__repr_name__()}"
                )
                return []

    def compare_and_update_claims(
        self,
        entity: Union[WikipediaPage, WikipediaPageReference],
        wikipedia_page: Optional[WikipediaPage] = None,
        wikibase_item: Optional[ItemEntity] = None,
    ) -> None:
        """We compare and update claims that are completely missing from the Wikibase item.
        We also remove reference claims no longer present in the Wikipedia page.
        :param entity is the entity to compare. Either a WikipediaPage or a WikipediaPageReference
        :param wikibase_item is used for offline testing only
        :param wikipedia_page is the page the reference belongs to"""
        logger.debug("compare_and_update_claims: Running")
        if not entity.wikibase_return:
            raise MissingInformationError("new_reference.wikibase_return was None")
        if entity.wikibase_return.uploaded_now:
            logger.info("Skipping comparison because the reference was just uploaded")
        else:
            wcr = WikibaseCrudRead(wikibase=self.wikibase)
            if isinstance(entity, WikipediaPageReference):
                if not wikipedia_page:
                    raise MissingInformationError("wikipedia_page was None")
                if entity.title:
                    console.print(
                        f"Comparing {entity.template_name} "
                        f"reference with the title '{entity.title}'"
                    )
                else:
                    console.print(
                        f"Comparing {entity.template_name} "
                        f"reference with missing title"
                    )
                logger.info(
                    f"See {self.wikibase.entity_url(item_id=entity.wikibase_return.item_qid)}"
                )
                new_item = wcr.__prepare_new_reference_item__(
                    page_reference=entity, wikipedia_page=wikipedia_page
                )
            else:
                logger.info(f"Comparing page with title '{entity.title}")
                new_item = wcr.__prepare_new_wikipedia_page_item__(
                    wikipedia_page=entity
                )
            if not wikibase_item:
                wikibase_item = wcr.get_item(item_id=entity.wikibase_return.item_qid)
                if not wikibase_item:
                    raise ValueError(
                        "Cannot compare because the "
                        "item was not found in the Wikibase. "
                        "This should never happen."
                    )
            if wikibase_item.claims == new_item.claims:
                console.print("The claims of the items are equal. No update needed.")
            else:
                self.__compare_claims_and_upload__(
                    entity=entity, wikibase_item=wikibase_item, new_item=new_item
                )
