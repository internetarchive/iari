from src import MissingInformationError
from src.models.v2.job import JobV2

class SignalsDocsJobV2(JobV2):
    """
    job for signals_docs endpoint
    """

    # use marshmallow to describe parameters
    # no parameters to describe

    def validate_fields(self):
        """
        check parameters here

        none to process

        """

        pass

