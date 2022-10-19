from enum import Enum


class Return(Enum):
    INVALID_QID = "Invalid Wikidata QID"
    NO_QID = "No Wikidata QID was given"
    NO_MATCH = "404: No match found for this Wikidata QID in the WikiCitations"
