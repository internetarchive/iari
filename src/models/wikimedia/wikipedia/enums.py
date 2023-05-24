from enum import Enum


class MalformedUrlError(Enum):
    MISSING_SCHEME = "missing scheme"
    UNRECOGNIZED_SCHEME = "unrecognized scheme"
    NO_NETLOC_FOUND = "no netloc found"
