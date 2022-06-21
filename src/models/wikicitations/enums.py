from enum import Enum

# WCD = WikiCitations Database


class KnownArchiveUrl(Enum):
    """Each value in this enum should have a corresponding attribute in the Wikibase class"""

    ARCHIVE_IS = "archive.is"
    ARCHIVE_ORG = "archive.org"
    ARCHIVE_PH = "archive.is"
    MEMENTOWEB_ORG = "mementoweb.org"
    ARCHIVE_TODAY = "archive.today"
    WEBCITATION_ORG = "webcitation.org"
