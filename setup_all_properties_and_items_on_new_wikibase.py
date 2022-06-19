"""
The purpose of this script is to setup all the properties we want in a new Wikibase
This could be fully automated but we don't need it often enough for it to be feasible
e.g. using a json file on disk which is read every time the bot runs.
We keep it simple and using a class will enable typing for the developer which is
a big plus :)
"""
import argparse
import logging
from typing import Any, Dict

from pydantic import BaseModel
from wikibaseintegrator import WikibaseIntegrator, datatypes, wbi_login  # type: ignore
from wikibaseintegrator.entities import ItemEntity  # type: ignore
from wikibaseintegrator.models import (  # type: ignore
    Claims,
    Descriptions,
    Labels,
    LanguageValue,
)
from wikibaseintegrator.wbi_enums import WikibaseDatatype  # type: ignore
from wikibaseintegrator.wbi_exceptions import MWApiError  # type: ignore

import config
from src.models.wikibase.dictionaries import (
    wcd_archive_items,
    wcd_items,
    wcd_properties,
    wcd_url_properties,
)
from src.models.wikibase.sandbox_wikibase import SandboxWikibase
from src.models.wikicitations import WikiCitations

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class SetupNewWikibase(BaseModel):
    wikibase = SandboxWikibase()

    def __setup_archive_items__(self):
        # They rely on each other so they have to be created in a certain order it seems
        # then the instance_of=archive item
        wc = WikiCitations(wikibase=self.wikibase)
        wc.__setup_wikibase_integrator_configuration__()
        wbi = WikibaseIntegrator(
            login=wbi_login.Login(
                user=wc.wikibase.user_name,
                password=wc.wikibase.botpassword,
                mediawiki_api_url=wc.wikibase.mediawiki_api_url,
            )
        )
        archive_item = wbi.item.new(
            labels=Labels().add(
                language_value=LanguageValue(language="en", value="Archive")
            ),
            descriptions=Descriptions().add(
                language_value=LanguageValue(language="en", value="web archive")
            ),
        )
        result = archive_item.write()
        archive_item_qid = result.id
        # then the individual archive organization items
        count = 1
        for item in wcd_archive_items:
            if count <= 1:
                data: Dict[Any, Any] = wcd_archive_items[item]
                description = data["description"]
                label = data["label"]
                draft_item = wbi.item.new(
                    labels=Labels().add(
                        language_value=LanguageValue(language="en", value=label)
                    ),
                    descriptions=Descriptions().add(
                        language_value=LanguageValue(language="en", value=description)
                    ),
                    # add claim to individual archive organization items
                    claims=Claims().add(
                        claims=[
                            # instance of
                            datatypes.Item(
                                prop_nr=self.wikibase.INSTANCE_OF,
                                value=archive_item_qid,
                            )
                        ]
                    ),
                )
                try:
                    new_item = draft_item.write()
                    print(
                        f'{item} = "{new_item.id}" # label: {label} description: {description}'
                    )
                except MWApiError as e:
                    logger.error(f"Got error: {e} from the Wikibase")
                count += 1
        # then save the QID of archive_item in memory

    @staticmethod
    def __setup_argparse_and_return_args__() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-i",
            "--items",
            action="store_true",
            help="Import the semantic items we need",
        )
        parser.add_argument(
            "-p",
            "--properties",
            action="store_true",
            help="Import the properties we need",
        )
        return parser.parse_args()

    def __setup_other_items__(self):
        # first create the wikipedia items
        wc = WikiCitations(wikibase=self.wikibase)
        wc.__setup_wikibase_integrator_configuration__()
        wbi = WikibaseIntegrator(
            login=wbi_login.Login(
                user=wc.wikibase.user_name,
                password=wc.wikibase.botpassword,
                mediawiki_api_url=wc.wikibase.mediawiki_api_url,
            )
        )
        count = 1
        for item in wcd_items:
            if count <= 1:
                data: Dict[Any, Any] = wcd_items[item]
                description = data["description"]
                label = data["label"]
                draft_item = wbi.item.new(
                    labels=Labels().add(
                        language_value=LanguageValue(language="en", value=label)
                    ),
                    descriptions=Descriptions().add(
                        language_value=LanguageValue(language="en", value=description)
                    ),
                )
                try:
                    new_item = draft_item.write()
                    print(
                        f'{item} = "{new_item.id}" # label: {label} description: {description}'
                    )
                except MWApiError as e:
                    logger.error(f"Got error: {e} from the Wikibase")
                count += 1

    def run(self):
        args = self.__setup_argparse_and_return_args__()
        if args.items is True:
            self.setup_items()
        if args.properties is True:
            self.setup_properties()
            input(
                f"Now copy the above output into the {snw.wikibase.__repr_name__()} "
                f"class. Afterwards kill and run this script again."
            )

    def setup_items(self):
        self.__setup_other_items__()
        self.__setup_archive_items__()

    def setup_properties(self):
        # iterate over the dictionary and create all the properties
        # output in a form that can be copy-pasted into a Wikibase class
        # (ie 'author = "P1"\nauthor_name_string = "P2"'
        wc = WikiCitations(wikibase=self.wikibase)
        wc.__setup_wikibase_integrator_configuration__()
        wbi = WikibaseIntegrator(
            login=wbi_login.Login(
                user=wc.wikibase.user_name,
                password=wc.wikibase.botpassword,
                mediawiki_api_url=wc.wikibase.mediawiki_api_url,
            )
        )
        count = 1
        for entry in wcd_properties + wcd_url_properties:
            if count <= 3:
                data: Dict[Any, Any] = wcd_properties[entry]
                datatype: WikibaseDatatype = data["datatype"]
                description = data["description"]
                label = entry.replace("_", " ").title()
                draft_property = wbi.property.new(
                    datatype=datatype.value,
                    labels=Labels().add(
                        language_value=LanguageValue(language="en", value=label)
                    ),
                    descriptions=Descriptions().add(
                        language_value=LanguageValue(language="en", value=description)
                    ),
                )
                try:
                    property = draft_property.write()
                    print(
                        f'{entry} = "{property.id}" # datatype: {datatype} description: {description}'
                    )
                except MWApiError as e:
                    logger.warning(f"Got error: {e} from the Wikibase")
                count += 1
        # manually copy-paste the output into a subclass of Wikibase


if __name__ == "__main__":
    print("First setup the properties and then the items. Use -h to see help.")
    snw = SetupNewWikibase()
    snw.run()
