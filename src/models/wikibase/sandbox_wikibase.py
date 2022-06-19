import config
from src.models.wikibase import Wikibase


class SandboxWikibase(Wikibase):
    """This models the properties on sandbox.wiki"""

    user_name = config.sandbox_user
    botpassword = config.sandbox_pwd

    wikibase_url = "https://sandbox.wiki"
    query_service_url = "https://query.sandbox.wiki"
    mediawiki_api_url: str = wikibase_url + "/w/api.php"
    mediawiki_index_url: str = wikibase_url + "/w/index.php"
    rdf_entity_prefix: str = wikibase_url + "/entity/"
    sparql_endpoint_url: str = query_service_url + "/query/sparql"

    ACCESS_DATE = ""
    ARCHIVE = ""
    ARCHIVE_DATE = ""
    ARCHIVE_URL = ""
    AUTHOR = ""
    FULL_NAME_STRING = ""
    DOI = ""
    EDITOR = ""
    EDITOR_NAME_STRING = ""
    FAMILY_NAME = ""
    GIVEN_NAME = ""
    CITATIONS = ""
    FIRST_LEVEL_DOMAIN_STRING = ""
    FULL_WORK_AVAILABLE_AT_URL = ""
    HASH = ""
    HOST_STRING = ""
    INSTANCE_OF = ""
    INTERVIEWER_STRING = ""
    ISBN_10 = ""
    ISBN_13 = ""
    ISSUE = ""
    LAST_UPDATE = ""
    LOCATION_STRING = ""
    LUMPED_AUTHORS = ""
    MEDIAWIKI_PAGE_ID = ""
    NAME_MASK = ""
    ORCID = ""
    PAGES = ""
    PMID = ""
    PUBLICATION_DATE = ""
    PUBLISHED_IN = ""
    PUBLISHER_STRING = ""
    RETRIEVED_DATE = ""
    PAGE_REVISION_ID = ""  # string
    SERIES_ORDINAL = ""  # aka author position # quantity
    SOURCE_WIKIPEDIA = ""
    STRING_CITATIONS = ""
    TEMPLATE_NAME = ""
    TITLE = ""  # monolingual text
    TRANSLATOR_NAME_STRING = ""
    URL = ""
    VOLUME = ""
    WEBSITE = ""
    WEBSITE_STRING = ""
    WIKIDATA_QID = ""  # external id

    CHAPTER_URL = ""
    CONFERENCE_URL = ""
    LAY_URL = ""
    TRANSCRIPT_URL = ""
