from pydantic import validate_arguments
from wikibaseintegrator.models import Claim  # type: ignore


@validate_arguments
def get_item_value(self, claim: Claim):
    return claim.mainsnak.datavalue["value"]["id"]


@validate_arguments
def get_time_value(self, claim: Claim):
    return claim.mainsnak.datavalue["value"]["time"]
