from enum import Enum

# WCD = WikiCitations Database


class KnownArchiveUrl(Enum):
    """Each value in this enum should have a corresponding entry in WCDItem"""

    ARCHIVE_IS = "archive.is"
    ARCHIVE_ORG = "archive.org"
    ARCHIVE_PH = "archive.is"
    MEMENTOWEB_ORG = "mementoweb.org"
    ARCHIVE_TODAY = "archive.today"
    WEBCITATION_ORG = "webcitation.org"


class WCDItem(Enum):
    ARCHIVE_IS = "Q5830"
    ARCHIVE_ORG = "Q5660"
    ARCHIVE_PH = "Q5830"
    ARCHIVE_TODAY = ""
    ENGLISH_WIKIPEDIA = "Q3"
    MEMENTOWEB_ORG = ""
    WEBCITATION_ORG = ""
    WEBSITE = "Q145"
    WIKIPEDIA_PAGE = "Q6"
    WIKIPEDIA_REFERENCE = "Q4"
