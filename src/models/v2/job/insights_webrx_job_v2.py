from typing import Optional
from pydantic import BaseModel

from src import MissingInformationError
from src.models.v2.job import JobV2


class InsightsWebRxJobV2(JobV2):
    """job that supports InsightsWebRxV2 endpoint"""

    # using marshmallow to describe parameters

    date_start: Optional[str] = None
    date_end: Optional[str] = None

    def validate_fields(self):
        """
        parameter checking here, if any
        """

        pass
