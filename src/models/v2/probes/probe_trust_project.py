from src.constants.constants import ProbeMethod

from src.models.v2.probes.iari_probe import IariProbeBase


class ProbeTrustProject(IariProbeBase):
    """
    "Implements" IariProbeBase class

    "probe" method returns json formatted probe results
    """

    @property
    def probe_name(self):
        return ProbeMethod.TRUST_PROJECT.value

    @staticmethod
    def probe(url):
        """
        returns results of trust_project probe for url
        """
        results = {
            "url": url
        }

        results.update({
            "errors": [
                "Trust Project probe not yet implemented"
            ]
        })

        return results

