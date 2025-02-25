from urllib.parse import unquote
from src.constants.constants import CheckMethod

from src.models.v2.job import JobV2


class CheckUrlJobV2(JobV2):

    url: str
    method: str = CheckMethod.LIVEWEBCHECK.value
    timeout: int = 2  # We default to 2 seconds

    @property
    def unquoted_url(self):
        """Decoded url"""
        return unquote(self.url)

    # check method; allow aliases
    def validate_fields(self):
        """
        any parameter checking done here...

        if method = WAYBACK then change to LIVEWEBCHECK
        """
        self.method = self.method.upper()
        if self.method == "WAYBACK" or self.method == "LWC":
            self.method = CheckMethod.LIVEWEBCHECK.value

        # any other exception go here, and raise exception for endpoint
