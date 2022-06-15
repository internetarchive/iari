"""
The purpose of this script is to setup all the properties we want in a new Wikibase
This could be fully automated but we don't need it often enough for it to be feasible
e.g. using a json file on disk which is read every time the bot runs.
We keep it simple and using a class will enable typing for the developer which is
a big plus :)
"""
import logging
from typing import Any, Dict

from wikibaseintegrator import WikibaseIntegrator, wbi_login  # type: ignore
from wikibaseintegrator.models import (  # type: ignore
    Descriptions,
    Labels,
    LanguageValue,
)
from wikibaseintegrator.wbi_enums import WikibaseDatatype  # type: ignore
from wikibaseintegrator.wbi_exceptions import MWApiError  # type: ignore

import config
from src.models.wikibase.dictionaries import wcd_properties
from src.models.wikibase.sandbox_wikibase import SandboxWikibase
from src.models.wikicitations import WikiCitations

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)

# iterate over the dictionary and create all the properties
# output in a form that can be copy-pasted into a Wikibase class
# (ie 'author = "P1"\nauthor_name_string = "P2"'
wc = WikiCitations(wikibase=SandboxWikibase())
wc.__setup_wikibase_integrator_configuration__()
wbi = WikibaseIntegrator(
    login=wbi_login.Login(
        user=wc.wikibase.user_name,
        password=wc.wikibase.botpassword,
        mediawiki_api_url=wc.wikibase.mediawiki_api_url,
    )
)
count = 1
for entry in wcd_properties:
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
            logger.error(f"Got error: {e} from the Wikibase")
        count += 1
# manually copy-paste the output into a subclass of Wikibase
