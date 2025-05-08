import pprint
from datetime import datetime
from typing import Any, Dict, List, Optional
import re
import logging
import requests

from src.constants.constants import ProbeMethod
from src.models.exceptions import MissingInformationError

from src.models.v2.probes.iari_probe import IariProbe


class ProbeVerifyi(IariProbe):
    """
    "Implements" IariProbe base class
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
        from IariProbe base class
        """
        return ProbeMethod.VERIFYI.value


    @staticmethod
    def probe(url):
        """
        from IariProbe base class

        returns results of verifyi probe for url
        currently, verifyi has two endpoints: assess and blocklist_check
        we collect info from both and put them all in the probe results
        """
        from src import app

        now = datetime.utcnow()
        results = {
            "url": url,
            "timestamp": datetime.timestamp(now),
            "isodate": now.isoformat(),
        }

        try:

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

                app.logger.debug(msg)

                results.setdefault('errors', []).append(msg)  # add or create errors entry

        except Exception as e:
            raise Exception(f"Unknown error while probing {url} with {ProbeVerifyi().probe_name}. args: {e.args}")


        # now do blocklist_check
        results.setdefault('errors', []).append("blocklist_check not yet implemented.")

        return results
