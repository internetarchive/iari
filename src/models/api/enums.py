from enum import Enum


class Lang(Enum):
    # We only support English for now
    en = "en"


# class Return(Enum):
#     INVALID_QID = "Invalid Wikidata QID"
#     NO_QID = "No Wikidata QID was given"
#     # https://www.geeksforgeeks.org/string-formatting-in-python/
#     NO_MATCH = "404: No match found for Wikidata QID {qid} in {wikibase}"
