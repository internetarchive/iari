import requests

from src.constants.constants import ProbeMethod
from src.models.v2.probes.iari_probe import IariProbe


class ProbeTest(IariProbe):
    """
    "Implements" IariProbe base class

    logic for obtaining probe results from specific probe

    what we need:
    link spec // or text later on, for a claim?

    what we return:
    json formatted probe results

    """

    # probe_name = ProbeMethod.TEST.value
    @property
    def probe_name(self):
        return ProbeMethod.TEST.value

    @staticmethod
    def probe(url):
        """
        returns results of verifyi probe for url
        """


        results = {
            "url": url
        }

        results.update({
            'message': f"TEST: Probing {url} with {ProbeTest().probe_name} probe"
        })


        return results


