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

    @property
    def probe_name(self):
        return ProbeMethod.VERIFYI.value

    @staticmethod
    def probe(url):
        """
        returns results of verifyi probe for url
        """

        results = {
            "url": url
        }

        user_agent = "IARI, see https://github.com/internetarchive/iari"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent
        }
        # TODO do we need to cleanse url here?

        response = requests.post(
            'https://trustproject.org/',
            headers=headers,
            json={'url': url})

        if response.status_code == 200:
            data = response.json()
            # TODO do some data transform here before adding results
            results.update(data)

        else:
            msg = f"Error probing {url} with {ProbeTrustProject().probe_name}. Got {response.status_code} from {url}"
            # raise Exception(
            #     f"Could not probe {self.url}. Got {response.status_code} from {url}"
            # )
            results.update({"message": msg})

        return results

