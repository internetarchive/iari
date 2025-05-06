from typing import Optional
from urllib.parse import unquote
from src.constants.constants import CheckMethod

from src.models.v2.job import JobV2


class GetUrlInfoJobV2(JobV2):
    """
    There are 3 types of information, called 'parts', that are supported now:
    'status' : provides url status and parsed information
    'probes' : gives all available probe information for all probe types specified
                by the probes parameter, which is a List of probes (probe names for now).
    'test' : should always give something, tho not specified at all what this should do...
    """

    url: str
    timeout: int = 2  # default to 2 seconds wait before timeout

    # parts: Optional[str] = "status|probes|test"  # pipe delimited list of parts to include. e.g.: "status|probes|test"
    parts: Optional[str]  # pipe delimited list of parts to include. e.g.: "status|probes|test"

    method: Optional[str] = CheckMethod.LIVEWEBCHECK.value
    # required when "status" specified in parts list

    probes: Optional[str] = None
    # pipe delimited list of probes
    # required when "probes" specified in parts list


    @property
    def unquoted_url(self):
        """Decoded url"""
        return unquote(self.url)

    @property
    def parts_list(self):

        _default_parts_list = ["status", "probes", "test"]  # TODO move this to constants module

        # if parts_list is None or not parts_list:
        #     parts_list = self._default_parts_list
        #

        """List version of part pipe-delimited string"""
        if not self.parts:
            return _default_parts_list
        return [item.strip() for item in self.parts.split('|') if item.strip()]

    def validate_fields(self):
        """
        any parameter checking done here...

        we allow aliases for check method:
            "WAYBACK" and "LWC" resolve to "LIVEWEBCHECK"

        """

        self.method = self.method.upper()
        if self.method == "WAYBACK" or self.method == "LWC":
            self.method = CheckMethod.LIVEWEBCHECK.value

        # any other endpoint exceptions go here...

