from src import MissingInformationError
from src.models.v2.job import JobV2


class RefInsightsJobV2(JobV2):
    """job that supports RefInsightsV2 endpoint"""

    # using marshmallow to describe parameters

    date_start: str = ""
    date_end: str = ""


    def validate_fields(self):
        """
        parameter checking here, if any
        """

        pass



