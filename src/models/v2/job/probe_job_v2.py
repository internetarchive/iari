from typing import Optional
from urllib.parse import unquote

from src import MissingInformationError
from src.constants.constants import ProbeMethod

from src.models.v2.job import JobV2


class ProbeJobV2(JobV2):
    url: str
    probe: Optional[str] = None  # specify just one probe
    probes: Optional[str] = None  # specify pipe delimited list of probes
    timeout: int = 2  # We default to 2 seconds

    probe_list: list = []

    @property
    def unquoted_url(self):
        """Decoded url"""
        return unquote(self.url)

    # check method; allow aliases
    def validate_fields(self):

        """
        must have either probes or probes defined.
        probes will take precedence
        self.<param_name> is param value from API call
        """

        # cannot have both probe and probes defined

        # cannot have both probe and probes defined
        if self.probe and self.probes:
            raise MissingInformationError(
                f"Either 'probe' or 'probes' param can be specified, but not both"
            )

        # we will use self.probes (pipe delimited version) going forward
        if not self.probes:
            if not self.probe:
                raise MissingInformationError(
                    f"Either probe or probes param must be specified"
                )
            self.probes = self.probe

        # either probe or probes must be specified
        self.probe_list = self.probes.split('|')
        if len(self.probe_list) == 0:
            raise MissingInformationError(
                f"At least one probe must be specified"
            )


