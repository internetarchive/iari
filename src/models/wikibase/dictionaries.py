from src.models.wikibase.enums import PropertyDatatype

# This dictionary is the master of all the properties we need for WikiCitations
wcd_properties = dict(
    ACCESS_DATE=dict(
        datatype=PropertyDatatype.DATE, description="date of access of the resource"
    ),
    ARCHIVE=dict(datatype=PropertyDatatype.ITEM, description=""),
    ARCHIVE_DATE=dict(datatype=PropertyDatatype.STRING, description=""),
    ARCHIVE_URL=dict(datatype=PropertyDatatype.URL, description=""),
    AUTHOR=dict(datatype=PropertyDatatype.ITEM, description=""),
    FULL_NAME_STRING=dict(datatype=PropertyDatatype.STRING, description=""),
    DOI=dict(datatype=PropertyDatatype.EXTERNAL_ID, description=""),
    EDITOR=dict(datatype=PropertyDatatype.ITEM, description=""),
    EDITOR_NAME_STRING=dict(datatype=PropertyDatatype.STRING, description=""),
    FAMILY_NAME=dict(datatype=PropertyDatatype.STRING, description=""),
    GIVEN_NAME=dict(datatype=PropertyDatatype.STRING, description=""),
    CITATIONS=dict(datatype=PropertyDatatype.ITEM, description=""),
    FIRST_LEVEL_DOMAIN_STRING=dict(datatype=PropertyDatatype.STRING, description=""),
    FULL_WORK_AVAILABLE_AT_URL=dict(datatype=PropertyDatatype.URL, description=""),
    HASH=dict(datatype=PropertyDatatype.STRING, description=""),
    HOST_STRING=dict(datatype=PropertyDatatype.STRING, description=""),
    INSTANCE_OF=dict(datatype=PropertyDatatype.ITEM, description=""),
    INTERVIEWER_STRING=dict(datatype=PropertyDatatype.STRING, description=""),
    ISBN_10=dict(datatype=PropertyDatatype.EXTERNAL_ID, description=""),
    ISBN_13=dict(datatype=PropertyDatatype.EXTERNAL_ID, description=""),
    ISSUE=dict(datatype=PropertyDatatype.STRING, description=""),
    LAST_UPDATE=dict(
        datatype=PropertyDatatype.DATE, description="date of last update of this item?"
    ),
    LOCATION_STRING=dict(datatype=PropertyDatatype.STRING, description=""),
    LUMPED_AUTHORS=dict(datatype=PropertyDatatype.STRING, description=""),
    MEDIAWIKI_PAGE_ID=dict(
        # this is string in WCD
        datatype=PropertyDatatype.EXTERNAL_ID,
        description="",
    ),
    NAME_MASK=dict(datatype=PropertyDatatype.STRING, description=""),
    ORCID=dict(datatype=PropertyDatatype.EXTERNAL_ID, description=""),
    PAGES=dict(datatype=PropertyDatatype.STRING, description=""),
    PMID=dict(datatype=PropertyDatatype.EXTERNAL_ID, description=""),
    PUBLICATION_DATE=dict(
        datatype=PropertyDatatype.DATE,
        description="date of publication of the resource",
    ),
    PUBLISHED_IN=dict(datatype=PropertyDatatype.STRING, description=""),
    PUBLISHER_STRING=dict(datatype=PropertyDatatype.STRING, description=""),
    RETRIEVED_DATE=dict(
        datatype=PropertyDatatype.DATE, description="date of retrieval of the resource"
    ),
    PAGE_REVISION_ID=dict(datatype=PropertyDatatype.STRING, description=""),
    SERIES_ORDINAL=dict(datatype=PropertyDatatype.QUANTITY, description=""),
    SOURCE_WIKIPEDIA=dict(datatype=PropertyDatatype.ITEM, description=""),
    STRING_CITATIONS=dict(datatype=PropertyDatatype.STRING, description=""),
    TEMPLATE_NAME=dict(datatype=PropertyDatatype.STRING, description=""),
    TITLE=dict(datatype=PropertyDatatype.STRING, description=""),
    TRANSLATOR_NAME_STRING=dict(datatype=PropertyDatatype.STRING, description=""),
    URL=dict(datatype=PropertyDatatype.URL, description=""),
    VOLUME=dict(datatype=PropertyDatatype.STRING, description=""),
    WEBSITE=dict(datatype=PropertyDatatype.ITEM, description=""),
    WEBSITE_STRING=dict(datatype=PropertyDatatype.STRING, description=""),
    WIKIDATA_QID=dict(datatype=PropertyDatatype.EXTERNAL_ID, description=""),
)
