from typing import Optional
from urllib.parse import unquote

from src import MissingInformationError
from src.models.v2.job import JobV2

from src.helpers.iari_utils import iari_extract_root_domain


class SignalsJobV2(JobV2):
    """
    job for signals endpoint
    """

    # use marshmallow to describe parameters
    domain: Optional[str] = None
    url: Optional[str] = None
    tag: Optional[str] = None

    @property
    def unquoted_url(self):
        """Decoded url"""
        return unquote(self.url) if self.url else None

    def validate_fields(self):
        """
        check parameters here

        if domain is provided, use that
        if url is provided, extract domain from url and use that
        if neither url nor domain is provided, raise error
        
        """

        # either probe or probes must be specified
        if not self.domain:
            if not self.url:
                raise MissingInformationError(
                    f"Either 'domain' or 'url' param must be specified."
                )
            else:  # url is defined but domain isn't - extract domain from url
                self.domain = iari_extract_root_domain(self.url)
        

