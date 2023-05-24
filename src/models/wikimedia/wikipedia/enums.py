from enum import Enum


class MalformedUrlError(Enum):
    MISSING_SCHEME = "missing scheme"
    UNRECOGNIZED_SCHEME = "unrecognized scheme"
    HTTPWWW = "fix httpwww -> http://www"
    HTTPSWWW = "fix httpswww -> https://www"
    NO_NETLOC_FOUND = "no netloc found"
