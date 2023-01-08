import config
from src.models.wikibase import Wikibase


class WikiCitationsWikibase(Wikibase):
    """This models the properties and items on wikicitations.wikibase.cloud"""

    title = "wikicitations.wikibase.cloud"
    user_name = config.user
    botpassword = config.pwd
    wikibase_url = "https://wikicitations.wikibase.cloud/"
    query_service_url = wikibase_url + "/query/"

    DOI = "P53"  # datatype: WikibaseDatatype.EXTERNALID description: None
    GOOGLE_BOOKS_ID = "P54"  # datatype: WikibaseDatatype.EXTERNALID description:
    # Identifier used to link books at Google.
    INTERNET_ARCHIVE_ID = "P55"  # datatype: WikibaseDatatype.EXTERNALID description:
    # Identifier used to link books and other resources at Internet Archive.
    ISBN_10 = "P56"  # datatype: WikibaseDatatype.EXTERNALID description: None
    ISBN_13 = "P57"  # datatype: WikibaseDatatype.EXTERNALID description: None
    MEDIAWIKI_PAGE_ID = "P58"  # datatype: WikibaseDatatype.EXTERNALID description: None
    OCLC_CONTROL_NUMBER = "P59"  # datatype: WikibaseDatatype.EXTERNALID description:
    # Online Computer Library Centers control number in Worldcat
    ORCID = "P60"  # datatype: WikibaseDatatype.EXTERNALID description: None
    PMID = "P61"  # datatype: WikibaseDatatype.EXTERNALID description: None
    WIKIDATA_QID = "P62"  # datatype: WikibaseDatatype.EXTERNALID description: None
    ARCHIVE = (
        "P52"  # datatype: WikibaseDatatype.ITEM description: recognized web archive
    )
    AUTHOR = "P64"  # datatype: WikibaseDatatype.ITEM description: None
    CITATIONS = "P65"  # datatype: WikibaseDatatype.ITEM description: None
    EDITOR = "P66"  # datatype: WikibaseDatatype.ITEM description: None
    INSTANCE_OF = "P67"  # datatype: WikibaseDatatype.ITEM description: None
    PUBLISHED_IN = "P68"  # datatype: WikibaseDatatype.ITEM description: None
    SOURCE_WIKIPEDIA = "P69"  # datatype: WikibaseDatatype.ITEM description: None
    WEBSITE = "P70"  # datatype: WikibaseDatatype.ITEM description: None
    SERIES_ORDINAL = "P71"  # datatype: WikibaseDatatype.QUANTITY description: None
    EDITOR_NAME_STRING = "P72"  # datatype: WikibaseDatatype.STRING description: None
    FAMILY_NAME = "P73"  # datatype: WikibaseDatatype.STRING description: None
    FIRST_LEVEL_DOMAIN_STRING = (
        "P74"  # datatype: WikibaseDatatype.STRING description: None
    )
    FULL_NAME_STRING = "P75"  # datatype: WikibaseDatatype.STRING description: None
    GIVEN_NAME = "P76"  # datatype: WikibaseDatatype.STRING description: None
    HASH = "P77"  # datatype: WikibaseDatatype.STRING description: None
    HOST_STRING = "P78"  # datatype: WikibaseDatatype.STRING description: None
    INTERVIEWER_STRING = "P79"  # datatype: WikibaseDatatype.STRING description: None
    ISSUE = "P80"  # datatype: WikibaseDatatype.STRING description: None
    LOCATION_STRING = "P81"  # datatype: WikibaseDatatype.STRING description: None
    LUMPED_AUTHORS = "P82"  # datatype: WikibaseDatatype.STRING description: None
    NAME_MASK = "P83"  # datatype: WikibaseDatatype.STRING description: None
    PAGES = "P84"  # datatype: WikibaseDatatype.STRING description: None
    PAGE_REVISION_ID = "P85"  # datatype: WikibaseDatatype.STRING description: None
    PERIODICAL_STRING = "P86"  # datatype: WikibaseDatatype.STRING description: None
    PUBLISHER_STRING = "P87"  # datatype: WikibaseDatatype.STRING description: None
    STRING_CITATIONS = "P88"  # datatype: WikibaseDatatype.STRING description: None
    TEMPLATE_NAME = "P89"  # datatype: WikibaseDatatype.STRING description: None
    TITLE = "P90"  # datatype: WikibaseDatatype.STRING description: None
    TRANSLATOR_NAME_STRING = (
        "P91"  # datatype: WikibaseDatatype.STRING description: None
    )
    VOLUME = "P92"  # datatype: WikibaseDatatype.STRING description: None
    WEBSITE_STRING = "P93"  # datatype: WikibaseDatatype.STRING description: None
    ACCESS_DATE = "P94"  # datatype: WikibaseDatatype.TIME description: date of access of the resource
    ARCHIVE_DATE = "P95"  # datatype: WikibaseDatatype.TIME description: None
    LAST_UPDATE = "P96"  # datatype: WikibaseDatatype.TIME description: date of last update of this item?
    PUBLICATION_DATE = "P97"  # datatype: WikibaseDatatype.TIME description: date of publication of the resource
    RETRIEVED_DATE = "P98"  # datatype: WikibaseDatatype.TIME description: date of retrieval of the resource
    ARCHIVE_URL = "P99"  # datatype: WikibaseDatatype.URL description: None
    CHAPTER_URL = "P100"  # datatype: WikibaseDatatype.URL description: None
    CONFERENCE_URL = "P101"  # datatype: WikibaseDatatype.URL description: None
    FULL_WORK_AVAILABLE_AT_URL = (
        "P102"  # datatype: WikibaseDatatype.URL description: None
    )
    LAY_URL = "P103"  # datatype: WikibaseDatatype.URL description: None
    TRANSCRIPT_URL = "P104"  # datatype: WikibaseDatatype.URL description: None
    URL = "P105"  # datatype: WikibaseDatatype.URL description: None

    ENGLISH_WIKIPEDIA = (
        "Q7973"  # label: English Wikipedia description: language version of Wikipedia
    )
    WEBSITE_ITEM = "Q7974"  # label: Website description: first level domain website found in Wikipedia
    WIKIPEDIA_PAGE = "Q7975"  # label: Wikipedia page description: page in a language version of Wikipedia
    WIKIPEDIA_REFERENCE = "Q7976"  # label: Wikipedia reference description: reference on a page in Wikipedia
    ARCHIVE_ITEM = "Q7977"  # label: Archive description: web archive
    ARCHIVE_IS = "Q7978"  # label: Archive.is description: web archive
    ARCHIVE_ORG = "Q7979"  # label: Archive.org description: web archive
    ARCHIVE_TODAY = "Q7980"  # label: Archive.today description: web archive
    GHOSTARCHIVE_ORG = "Q7981"  # label: Ghostarchive.org description: web archive
    WEBCITATION_ORG = "Q7982"  # label: Webcitation.org description: web archive

    RAW_TEMPLATE = ""  # not setup yet

    # This has to come last to work.
    wcdqid_language_edition_of_wikipedia_to_work_on = ENGLISH_WIKIPEDIA
