import logging

from pydantic import validate_arguments
from wikibaseintegrator import wbi_login  # type: ignore
from wikibaseintegrator.wbi_exceptions import NonExistentEntityError  # type: ignore
from wikibaseintegrator.wbi_helpers import delete_page  # type: ignore

import config
from src.helpers import console, press_enter_to_continue
from src.models.wikibase.crud import WikibaseCrud
from src.models.wikibase.crud.read import WikibaseCrudRead

logger = logging.getLogger(__name__)


class WikibaseCrudDelete(WikibaseCrud):
    # TODO refactor delete_* methods into one using a BaseItemType
    def __delete_all_page_items__(self) -> None:
        """Get all items and delete them one by one"""
        read = WikibaseCrudRead(wikibase=self.wikibase)
        items = read.__get_all_page_items__() or []
        if items:
            self.__setup_wikibase_integrator_configuration__()
            with console.status(f"Deleting all page items"):
                count = 0
                for item_id in items:
                    logger.info(f"Deleting {item_id}")
                    self.__delete_item__(item_id=item_id)
                    # logger.debug(result)
                    if config.press_enter_to_continue:
                        press_enter_to_continue()
                    count += 1
                console.print(f"Done deleting a total of {count} page items")
        else:
            console.print("Got no page items from the WCD Query Service.")

    def __delete_all_reference_items__(self) -> None:
        """Get all items and delete them one by one"""
        read = WikibaseCrudRead(wikibase=self.wikibase)
        items = read.__get_all_reference_items__() or []
        if items:
            self.__setup_wikibase_integrator_configuration__()
            with console.status(f"Deleting all reference items"):
                count = 0
                for item_id in items:
                    logger.info(f"Deleting {item_id}")
                    self.__delete_item__(item_id=item_id)
                    # logger.debug(result)
                    if config.press_enter_to_continue:
                        press_enter_to_continue()
                    count += 1
            console.print(f"Done deleting a total of {count} reference items")
        else:
            console.print("Got no reference items from the WCD Query Service.")

    def __delete_all_website_items__(self):
        """Get all items and delete them one by one"""
        read = WikibaseCrudRead(wikibase=self.wikibase)
        items = read.__get_all_website_items__() or []
        if items:
            self.__setup_wikibase_integrator_configuration__()
            with console.status(f"Deleting all website items"):
                count = 0
                for item_id in items:
                    logger.info(f"Deleting {item_id}")
                    self.__delete_item__(item_id=item_id)
                    # logger.debug(result)
                    if config.press_enter_to_continue:
                        press_enter_to_continue()
                    count += 1
            console.print(f"Done deleting a total of {count} website items")
        else:
            console.print("Got no website items from the WCD Query Service.")

    @validate_arguments
    def __delete_item__(self, item_id: str):
        if config.press_enter_to_continue:
            input(f"Do you want to delete {item_id}?")
        logger.debug(f"trying to log in to the wikibase as {self.wikibase.user_name}")
        self.__setup_wikibase_integrator_configuration__()
        try:
            return delete_page(
                title=f"Item:{item_id}",
                # deletetalk=True,
                login=wbi_login.Login(
                    user=self.wikibase.user_name,
                    password=self.wikibase.botpassword,
                    mediawiki_api_url=self.wikibase.mediawiki_api_url,
                ),
            )
        except NonExistentEntityError:
            return

    def delete_imported_items(self):
        """This function deletes all the imported items in WikiCitations"""
        console.print("Deleting all imported items")
        self.__delete_all_page_items__()
        self.__delete_all_reference_items__()
        self.__delete_all_website_items__()
