"""
The purpose of this script is to setup all the properties we want in a new Wikibase
This could be fully automated but we don't need it often enough for it to be feasible
e.g. using a json file on disk which is read every time the bot runs.
We keep it simple and using a class will enable typing for the developer which is
a big plus :)
"""
from wikibaseintegrator import WikibaseIntegrator, wbi_login # type: ignore

from src.models.exceptions import DebugExit
from src.models.wikibase.dictionaries import wcd_properties
from src.models.wikibase.sandbox_wikibase import SandboxWikibase
from src.models.wikicitations import WikiCitations

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
for entry in wcd_properties:
    data = wcd_properties[entry]
    datatype = data["type"]
    description = data["description"]
    draft_property = wbi.property.new(
        datadatatype=type, label=entry.title(), description=description
    )
    property = draft_property.write()
    print(
        f'{entry} = "{property.id}" # datatype: {datatype} description: {description}'
    )
    DebugExit()
# manually copy-paste the output into a subclass of Wikibase
