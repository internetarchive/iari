from typing import Optional
from pydantic import BaseModel

from src import MissingInformationError
from src.models.v2.job import JobV2


class WikiSignalsJobV2(JobV2):
    """job that supports WikiSignalsV2 endpoint"""

    # using marshmallow to describe parameters

    domain: str


    def validate_fields(self):
        """
        parameter checking here, if any

        set self.domain to extracted domain of passed in domain if domain is a url, and
        but just a domain name.
        """

        # extract domain name no matter what and set it.
        # NB TODO is  this where we parse domain name out of domain parameter and error if not found?
        pass



