from src import MissingInformationError
from src.models.v2.job import JobV2


class GetArchiveInfoJobV2(JobV2):
    """
    job that supports GetArchiveInfoJobV2 endpoint
    """

    # using marshmallow to describe parameters

    url: str
    timeout: int = 2  # default to 2 seconds wait before timeout

    # parts: Optional[str] = "wayback|other_archive_1|other_archive_2"

    def validate_fields(self):
        """
        parameter checking here...
        """

        pass  # do nothing right now

