from enum import Enum


# Enums for check-url method
class CheckMethod(Enum):
    IABOT = "IABOT"
    LIVEWEBCHECK = "LIVEWEBCHECK"
    CORENTIN = "CORENTIN"


# Enums for probe methods
class ProbeMethod(Enum):
    VERIFYI = "VERIFYI"
    TRUST_PROJECT = "TRUST_PROJECT"
    TEST = "TEST"
