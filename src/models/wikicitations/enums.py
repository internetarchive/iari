from enum import Enum

# WCD = WikiCitations Database


class KnownArchiveUrl(Enum):
    """Each value in this enum should have a corresponding attribute in the Wikibase class"""

    ARCHIVE_IS = "archive.is"
    ARCHIVE_ORG = "archive.org"
    ARCHIVE_PH = "archive.is"
    ARCHIVE_TODAY = "archive.today"
    GHOSTARCHIVE_ORG = "ghostarchive.org"
    MEMENTOWEB_ORG = "mementoweb.org"
    WEBCITATION_ORG = "webcitation.org"
