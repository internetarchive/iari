from enum import Enum


# Enums for check-url method
class CheckMethod(Enum):  # TODO this should eventually be eliminated when check_url is deprecated
    IABOT = "IABOT"
    LIVEWEBCHECK = "LIVEWEBCHECK"
    CORENTIN = "CORENTIN"


# Enums for URL info parts
class UrlInfoParts(Enum):
    STATUS = "STATUS"
    PROBES = "PROBES"
    TEST = "TEST"


# Enums for check-url method
class UrlStatusMethod(Enum):
    IABOT = "IABOT"
    LIVEWEBCHECK = "LIVEWEBCHECK"
    CORENTIN = "CORENTIN"


# Enums for probe methods
class ProbeMethod(Enum):
    VERIFYI = "VERIFYI"
    TRUST_PROJECT = "TRUST_PROJECT"
    TEST = "TEST"
    IFFY = "IFFY"
