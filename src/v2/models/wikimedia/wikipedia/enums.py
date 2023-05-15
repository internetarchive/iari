from enum import Enum


class MalformedUrlError(Enum):
    UNRECOGNIZED_TLD_LENGTH = "unrecognized tld length"
    MISSING_SCHEME = "missing scheme"
    UNRECOGNIZED_SCHEME = "unrecognized scheme"
    HTTPWWW = "fix httpwww -> http://www"
    HTTPSWWW = "fix httpswww -> https://www"
    NO_NETLOC_FOUND = "no netloc found"
