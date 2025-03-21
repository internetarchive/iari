from typing import Any, Dict, List, Optional
import re
import logging
import requests

from src.constants.constants import ProbeMethod
from src.models.exceptions import MissingInformationError

from src.models.v2.probes.iari_probe import IariProbe


class ProbeTrustProject(IariProbe):
    """
    "Implements" IariProbe base class

    logic for obtaining probe results from specific probe

    what we need:
    link spec // or text later on, for a claim?

    what we return:
    json formatted probe results

    """
    probe_name: str = ProbeMethod.TRUST_PROJECT.value
    url: str


    def probe(self):
        """
        returns results of trust_project probe for url
        """


        user_agent = "IARI, see https://github.com/internetarchive/iari"
        probe_api_url = (
            f"https://trustproject.com/"
            f"?url={self.url}"
        )
        headers = {"User-Agent": user_agent}
        response = requests.get(probe_api_url, headers=headers)

        results = {}

        if response.status_code == 200:
            data = response.json()
            # TODO may have to transform data before adding as results
            results.update(data)

        else:
            msg = f"Error probing {self.url} with {self.probe_name} . Got {response.status_code} from {probe_api_url}"
            # raise Exception(
            #     f"Could not probe {self.url}. Got {response.status_code} from {url}"
            # )
            results.update({"message": msg})

        return results

