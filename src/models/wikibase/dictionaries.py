"""
This file holds all the data about our needed properties and semantic "base" items.

One item is missing here and hardcoded into
setup_all_properties_and_items_on_new_wikibase.py for now
"""
from wikibaseintegrator.wbi_enums import WikibaseDatatype  # type: ignore

wcd_archive_items = dict(
    ARCHIVE_IS=dict(label="Archive.is", description="web archive"),
    ARCHIVE_ORG=dict(label="Archive.org", description="web archive"),
    ARCHIVE_TODAY=dict(label="Archive.today", description="web archive"),
    WEBCITATION_ORG=dict(label="Webcitation.org", description="web archive"),
)

wcd_items = dict(
    ENGLISH_WIKIPEDIA=dict(
        label="English Wikipedia", description="language version of Wikipedia"
    ),
    WEBSITE_ITEM=dict(
        label="Website", description="first level domain website found in Wikipedia"
    ),
    WIKIPEDIA_PAGE=dict(
        label="Wikipedia page", description="page in a language version of Wikipedia"
    ),
    WIKIPEDIA_REFERENCE=dict(
        label="Wikipedia reference", description="reference on a page in Wikipedia"
    ),
)


wcd_properties = dict(
    ACCESS_DATE=dict(
        datatype=WikibaseDatatype.TIME, description="date of access of the resource"
    ),
    ARCHIVE=dict(datatype=WikibaseDatatype.ITEM, description=""),
    ARCHIVE_DATE=dict(datatype=WikibaseDatatype.TIME, description=""),
    AUTHOR=dict(datatype=WikibaseDatatype.ITEM, description=""),
    FULL_NAME_STRING=dict(datatype=WikibaseDatatype.STRING, description=""),
    DOI=dict(datatype=WikibaseDatatype.EXTERNALID, description=""),
    EDITOR=dict(datatype=WikibaseDatatype.ITEM, description=""),
    EDITOR_NAME_STRING=dict(datatype=WikibaseDatatype.STRING, description=""),
    FAMILY_NAME=dict(datatype=WikibaseDatatype.STRING, description=""),
    GIVEN_NAME=dict(datatype=WikibaseDatatype.STRING, description=""),
    CITATIONS=dict(datatype=WikibaseDatatype.ITEM, description=""),
    FIRST_LEVEL_DOMAIN_STRING=dict(datatype=WikibaseDatatype.STRING, description=""),
    FULL_WORK_AVAILABLE_AT_URL=dict(datatype=WikibaseDatatype.URL, description=""),
    HASH=dict(datatype=WikibaseDatatype.STRING, description=""),
    HOST_STRING=dict(datatype=WikibaseDatatype.STRING, description=""),
    INSTANCE_OF=dict(datatype=WikibaseDatatype.ITEM, description=""),
    INTERVIEWER_STRING=dict(datatype=WikibaseDatatype.STRING, description=""),
    ISBN_10=dict(datatype=WikibaseDatatype.EXTERNALID, description=""),
    ISBN_13=dict(datatype=WikibaseDatatype.EXTERNALID, description=""),
    ISSUE=dict(datatype=WikibaseDatatype.STRING, description=""),
    LAST_UPDATE=dict(
        datatype=WikibaseDatatype.TIME, description="date of last update of this item?"
    ),
    LOCATION_STRING=dict(datatype=WikibaseDatatype.STRING, description=""),
    LUMPED_AUTHORS=dict(datatype=WikibaseDatatype.STRING, description=""),
    MEDIAWIKI_PAGE_ID=dict(
        # this is string in WCD
        datatype=WikibaseDatatype.EXTERNALID,
        description="",
    ),
    NAME_MASK=dict(datatype=WikibaseDatatype.STRING, description=""),
    ORCID=dict(datatype=WikibaseDatatype.EXTERNALID, description=""),
    PAGES=dict(datatype=WikibaseDatatype.STRING, description=""),
    PMID=dict(datatype=WikibaseDatatype.EXTERNALID, description=""),
    PUBLICATION_DATE=dict(
        datatype=WikibaseDatatype.TIME,
        description="date of publication of the resource",
    ),
    PUBLISHED_IN=dict(datatype=WikibaseDatatype.ITEM, description=""),
    PUBLISHER_STRING=dict(datatype=WikibaseDatatype.STRING, description=""),
    RETRIEVED_DATE=dict(
        datatype=WikibaseDatatype.TIME, description="date of retrieval of the resource"
    ),
    PAGE_REVISION_ID=dict(datatype=WikibaseDatatype.STRING, description=""),
    SERIES_ORDINAL=dict(datatype=WikibaseDatatype.QUANTITY, description=""),
    SOURCE_WIKIPEDIA=dict(datatype=WikibaseDatatype.ITEM, description=""),
    STRING_CITATIONS=dict(datatype=WikibaseDatatype.STRING, description=""),
    TEMPLATE_NAME=dict(datatype=WikibaseDatatype.STRING, description=""),
    TITLE=dict(datatype=WikibaseDatatype.STRING, description=""),
    TRANSLATOR_NAME_STRING=dict(datatype=WikibaseDatatype.STRING, description=""),
    VOLUME=dict(datatype=WikibaseDatatype.STRING, description=""),
    WEBSITE=dict(datatype=WikibaseDatatype.ITEM, description=""),
    WEBSITE_STRING=dict(datatype=WikibaseDatatype.STRING, description=""),
    WIKIDATA_QID=dict(datatype=WikibaseDatatype.EXTERNALID, description=""),
)

wcd_url_properties = dict(
    ARCHIVE_URL=dict(datatype=WikibaseDatatype.URL, description=""),
    CHAPTER_URL=dict(datatype=WikibaseDatatype.URL, description=""),
    CONFERENCE_URL=dict(datatype=WikibaseDatatype.URL, description=""),
    LAY_URL=dict(datatype=WikibaseDatatype.URL, description=""),
    TRANSCRIPT_URL=dict(datatype=WikibaseDatatype.URL, description=""),
    URL=dict(datatype=WikibaseDatatype.URL, description=""),
)
