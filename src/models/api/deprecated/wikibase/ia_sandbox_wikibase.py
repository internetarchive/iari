# import config
# from src.models.wikibase import Wikibase
#
#
# class IASandboxWikibase(Wikibase):
#     """This models the properties and items on ia-sandbox.wikibase.cloud/"""
#
#     botpassword = config.sandbox_pwd
#     title = "ia-sandbox.wikibase.cloud/"
#     user_name = config.sandbox_user
#     wikibase_url = "https://ia-sandbox.wikibase.cloud/"
#     wikibase_cloud_wikibase = True
#     query_service_url = wikibase_url + "/query/"
#
#     # Properties
#     DOI = "P1"  # datatype: WikibaseDatatype.EXTERNALID description:
#     GOOGLE_BOOKS_ID = "P2"  # datatype: WikibaseDatatype.EXTERNALID description:
#     # Identifier used to link books at Google.
#     INTERNET_ARCHIVE_ID = "P3"  # datatype: WikibaseDatatype.EXTERNALID description:
#     # Identifier used to link books and other resources at Internet Archive.
#     ISBN_10 = "P4"  # datatype: WikibaseDatatype.EXTERNALID description:
#     ISBN_13 = "P5"  # datatype: WikibaseDatatype.EXTERNALID description:
#     MEDIAWIKI_PAGE_ID = "P6"  # datatype: WikibaseDatatype.EXTERNALID description:
#     OCLC_CONTROL_NUMBER = "P7"  # datatype: WikibaseDatatype.EXTERNALID description:
#     # Online Computer Library Centers control number in Worldcat
#     ORCID = "P8"  # datatype: WikibaseDatatype.EXTERNALID description:
#     PMID = "P9"  # datatype: WikibaseDatatype.EXTERNALID description:
#     WIKIDATA_QID = "P10"  # datatype: WikibaseDatatype.EXTERNALID description:
#     ARCHIVE = "P11"  # datatype: WikibaseDatatype.ITEM description:
#     AUTHOR = "P12"  # datatype: WikibaseDatatype.ITEM description:
#     CITATIONS = "P13"  # datatype: WikibaseDatatype.ITEM description:
#     EDITOR = "P14"  # datatype: WikibaseDatatype.ITEM description:
#     INSTANCE_OF = "P15"  # datatype: WikibaseDatatype.ITEM description:
#     PUBLISHED_IN = "P16"  # datatype: WikibaseDatatype.ITEM description:
#     SOURCE_WIKIPEDIA = "P17"  # datatype: WikibaseDatatype.ITEM description:
#     WEBSITE = "P18"  # datatype: WikibaseDatatype.ITEM description:
#     SERIES_ORDINAL = "P19"  # datatype: WikibaseDatatype.QUANTITY description:
#     EDITOR_NAME_STRING = "P20"  # datatype: WikibaseDatatype.STRING description:
#     FAMILY_NAME = "P21"  # datatype: WikibaseDatatype.STRING description:
#     FIRST_LEVEL_DOMAIN_STRING = "P22"  # datatype: WikibaseDatatype.STRING description:
#     FULL_NAME_STRING = (
#         "P23"  # datatype: WikibaseDatatype.STRING description: author name string
#     )
#     GIVEN_NAME = "P24"  # datatype: WikibaseDatatype.STRING description:
#     HASH = "P25"  # datatype: WikibaseDatatype.STRING description:
#     HOST_STRING = "P26"  # datatype: WikibaseDatatype.STRING description:
#     INTERVIEWER_STRING = "P27"  # datatype: WikibaseDatatype.STRING description:
#     ISSUE = "P28"  # datatype: WikibaseDatatype.STRING description:
#     LOCATION_STRING = "P29"  # datatype: WikibaseDatatype.STRING description:
#     LUMPED_AUTHORS = "P30"  # datatype: WikibaseDatatype.STRING description:
#     NAME_MASK = "P31"  # datatype: WikibaseDatatype.STRING description:
#     PAGES = "P32"  # datatype: WikibaseDatatype.STRING description:
#     PAGE_REVISION_ID = "P33"  # datatype: WikibaseDatatype.STRING description:
#     PERIODICAL_STRING = "P34"  # datatype: WikibaseDatatype.STRING description:
#     PUBLISHER_STRING = "P35"  # datatype: WikibaseDatatype.STRING description:
#     RAW_TEMPLATE = "P89"  # datatype: WikibaseDatatype.STRING description:
#     STRING_CITATIONS = "P36"  # datatype: WikibaseDatatype.STRING description:
#     TEMPLATE_NAME = "P37"  # datatype: WikibaseDatatype.STRING description:
#     TITLE = "P38"  # datatype: WikibaseDatatype.STRING description:
#     TRANSLATOR_NAME_STRING = "P39"  # datatype: WikibaseDatatype.STRING description:
#     VOLUME = "P40"  # datatype: WikibaseDatatype.STRING description:
#     WEBSITE_STRING = "P41"  # datatype: WikibaseDatatype.STRING description:
#     ACCESS_DATE = "P42"  # datatype: WikibaseDatatype.TIME description: date of access of the resource
#     ARCHIVE_DATE = "P43"  # datatype: WikibaseDatatype.TIME description:
#     LAST_UPDATE = "P44"  # datatype: WikibaseDatatype.TIME description: date of last update of this item?
#     PUBLICATION_DATE = "P45"  # datatype: WikibaseDatatype.TIME description: date of publication of the resource
#     RETRIEVED_DATE = "P46"  # datatype: WikibaseDatatype.TIME description: date of retrieval of the resource
#     ARCHIVE_URL = "P47"  # datatype: WikibaseDatatype.URL description:
#     CHAPTER_URL = "P48"  # datatype: WikibaseDatatype.URL description:
#     CONFERENCE_URL = "P49"  # datatype: WikibaseDatatype.URL description:
#     FULL_WORK_AVAILABLE_AT_URL = "P50"  # datatype: WikibaseDatatype.URL description:
#     LAY_URL = "P51"  # datatype: WikibaseDatatype.URL description:
#     TRANSCRIPT_URL = "P52"  # datatype: WikibaseDatatype.URL description:
#     URL = "P53"  # datatype: WikibaseDatatype.URL description:
#
#     # Items
#     ENGLISH_WIKIPEDIA = (
#         "Q17"  # label: English Wikipedia description: language version of Wikipedia
#     )
#     WEBSITE_ITEM = "Q18"  # label: Website description: first level domain website found in Wikipedia
#     WIKIPEDIA_PAGE = "Q19"  # label: Wikipedia page description: page in a language version of Wikipedia
#     WIKIPEDIA_REFERENCE = "Q20"  # label: Wikipedia reference description: reference on a page in Wikipedia
#     ARCHIVE_ITEM = "Q21"  # label: Archive description: web archive
#     ARCHIVE_IS = "Q22"  # label: Archive.is description: web archive
#     ARCHIVE_ORG = "Q23"  # label: Archive.org description: web archive
#     ARCHIVE_TODAY = "Q24"  # label: Archive.today description: web archive
#     GHOSTARCHIVE_ORG = "Q25"  # label: Ghostarchive.org description: web archive
#     WEBCITATION_ORG = "Q26"  # label: Webcitation.org description: web archive
#
#     # This must come last to avoid errors
#     wcdqid_language_edition_of_wikipedia_to_work_on = ENGLISH_WIKIPEDIA
