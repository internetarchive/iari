from src.wcd_base_model import WcdBaseModel


class Wikibase(WcdBaseModel):
    """This is a parent class for the wikibases we support
    We define all the properties here to be able to use them in the subclasses"""

    user_name: str
    botpassword: str
    wikibase_url: str
    mediawiki_api_url: str
    mediawiki_index_url: str
    rdf_entity_prefix: str
    sparql_endpoint_url: str

    ACCESS_DATE: str  # date
    ARCHIVE: str  # item
    ARCHIVE_DATE: str  # date
    ARCHIVE_URL: str  # url
    AUTHOR: str  # item
    FULL_NAME_STRING: str  # string
    DOI: str  # external-id
    EDITOR: str  # item
    EDITOR_NAME_STRING: str  # string
    FAMILY_NAME: str  # string
    GIVEN_NAME: str  # string
    CITATIONS: str  # item
    FIRST_LEVEL_DOMAIN_STRING: str  # string
    FULL_WORK_AVAILABLE_AT_URL: str  # url
    HASH: str  # string
    HOST_STRING: str  # string
    INSTANCE_OF: str  # item
    INTERVIEWER_STRING: str  # string
    ISBN_10: str  # external-id
    ISBN_13: str  # external-id
    ISSUE: str  # string
    LAST_UPDATE: str  # date
    LOCATION_STRING: str  # string
    LUMPED_AUTHORS: str  # string
    MEDIAWIKI_PAGE_ID: str  # string # FIXME should be external-id
    NAME_MASK: str  # string
    ORCID: str  # external-id
    PAGES: str  # string
    PMID: str  # external-id
    PUBLICATION_DATE: str  # date
    PUBLISHED_IN: str  # ?
    PUBLISHER_STRING: str  # string
    RETRIEVED_DATE: str  # date
    PAGE_REVISION_ID: str  # string
    SERIES_ORDINAL: str  # aka author position # quantity
    SOURCE_WIKIPEDIA: str  # item
    STRING_CITATIONS: str  # string
    TEMPLATE_NAME: str  # string
    TITLE: str  # monolingual text
    TRANSLATOR_NAME_STRING: str  # string
    URL: str  # url
    VOLUME: str  # string
    WEBSITE: str  # item
    WEBSITE_STRING: str  # string
    WIKIDATA_QID: str  # external id
