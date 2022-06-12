from enum import Enum

# WCD = WikiCitations Database


class KnownArchiveUrl(Enum):
    """Each value in this enum should have a corresponding entry in WCDItem"""

    ARCHIVE_IS = "archive.is"
    ARCHIVE_ORG = "archive.org"
    ARCHIVE_PH = "archive.is"
    MEMENTOWEB_ORG = "mementoweb.org"


class WCDItem(Enum):
    ARCHIVE_IS = "Q5830"
    ARCHIVE_PH = "Q5830"
    ARCHIVE_ORG = "Q5660"
    ENGLISH_WIKIPEDIA = "Q3"
    MEMENTOWEB_ORG = ""
    WEBSITE = "Q145"
    WIKIPEDIA_REFERENCE = "Q4"
    WIKIPEDIA_PAGE = "Q6"
