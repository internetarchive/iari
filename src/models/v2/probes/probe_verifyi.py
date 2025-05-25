from datetime import datetime
import requests

from src.constants.constants import ProbeMethod

from src.models.v2.probes.iari_probe import IariProbeBase


class ProbeVerifyi(IariProbeBase):
    """
    "Implements" IariProbeBase class
    - probe_name property
    - probe method

    logic for obtaining probe results from specific probe

    what we need:
    link spec // or text later on, for a claim?

    what we return:
    json formatted probe results

    """

    @property
    def probe_name(self):
        """
        from IariProbeBase class
        """
        return ProbeMethod.VERIFYI.value


    @staticmethod
    def probe(url):
        """
        from IariProbeBase class

        returns results of verifyi probe for url
        currently, verifyi has two endpoints: assess and blocklist_check
        we collect info from both and put them all in the probe results
        """


        now = datetime.utcnow()
        results = {
            "url": url,
            "timestamp": datetime.timestamp(now),
            "isodate": now.isoformat(),
        }

        try:
            results.update(ProbeVerifyi().probe_assess(url))

        except Exception as e:
            # raise Exception(f"Unknown error while probing {url} with {ProbeVerifyi().probe_name}:  args: {e.args}")
            raise Exception(f"Unknown error while probing {url} with {ProbeVerifyi().probe_name}: {str(e)}")

        # now do blocklist_check
        results.setdefault('warnings', []).append("blocklist_check not yet implemented.")

        return results

    @staticmethod
    def probe_assess(url):

        results = {}

        user_agent = "IARI, see https://github.com/internetarchive/iari"
        headers = {
            # "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent
        }

        # do "assess" endpoint
        probe_api_url = 'https://veri-fyi.toolforge.org/assess'

        # TODO do we need to clean url param here?
        response = requests.post(
            probe_api_url,
            headers=headers,
            json={'url': url})

        if response.status_code == 200:
            data = response.json()
            results['raw'] = data
            # TODO do some data transform here to add to results, maybe results['processed']?

        else:
            # append error to errors array
            msg = (
                f"Error probing {url} with {ProbeVerifyi().probe_name} assess endpoint. "
                f" Got {response.status_code} from {probe_api_url}"
                f" Text: {response.text}"
            )

            from src import app
            app.logger.debug(msg)

            results.setdefault('errors', []).append(msg)  # add or create errors entry

        return results

    @staticmethod
    def probe_blocklist(url):

        results = {}

        user_agent = "IARI, see https://github.com/internetarchive/iari"
        headers = {
            # "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent
        }

        # do "assess" endpoint
        probe_api_url = 'https://veri-fyi.toolforge.org/blocklist'

        # TODO do we need to clean url param here?
        response = requests.post(
            probe_api_url,
            headers=headers,
            json={'url': url})

        if response.status_code == 200:
            data = response.json()
            results['raw_blocklist'] = data

        else:
            # append error to errors array
            msg = (
                f"Error probing {url} with {ProbeVerifyi().probe_name} assess endpoint. "
                f" Got {response.status_code} from {probe_api_url}"
                f" Text: {response.text}"
            )

            from src import app
            app.logger.debug(msg)

            results.setdefault('errors', []).append(msg)  # add or create errors entry

        return results

