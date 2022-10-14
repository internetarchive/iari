from pydantic import validate_arguments
from wikibaseintegrator.models import Claim  # type: ignore

# https://stackoverflow.com/questions/68349150/best-practice-to-pydantic-validate-arguments-for-non-built-in-types-like-pandas
@validate_arguments(config=dict(arbitrary_types_allowed=True))
def get_item_value(self, claim: Claim):
    return claim.mainsnak.datavalue["value"]["id"]


@validate_arguments(config=dict(arbitrary_types_allowed=True))
def get_time_value(self, claim: Claim):
    return claim.mainsnak.datavalue["value"]["time"]
