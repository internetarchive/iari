# probe_utils.py
import requests
from typing import Optional, Union

from src.helpers.cache_utils import get_cache, set_cache, is_cached, CacheType

from src.constants.constants import ProbeMethod
from src.models.v2.probes.probe_test import ProbeTest
from src.models.v2.probes.probe_trust_project import ProbeTrustProject
from src.models.v2.probes.probe_verifyi import ProbeVerifyi


class WikiUtils:

    @staticmethod
    def run_wiki_logic(data):
        # complex logic here
        return {"result": "ok"}



    @staticmethod
    def get_exturls():
        """
        returns wiki stats for external urls
        returns {
            stuff, stuff, stuff
        }

        """
        from src import app
        app.logger.debug(f"==> get_exturls_data")

        results = {}
        from_cache = False

        # fetch external url data
        results = WikiUtils.get_exturls_data()

        # set cached data...but not for now

        return {
            "external_urls": results,
        }


    def get_exturls_data():

        results = {}

        user_agent = "IARI, see https://github.com/internetarchive/iari"
        headers = {
            # "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent
        }

        # do "assess" endpoint
        exturls_api_url = 'https://commons.wikimedia.org/w/index.php?title=Data%3AWikipedia%5Fstatistics%2Fexturls%2Etab&action=raw'

        # TODO do we need to clean url param here?
        response = requests.get(
            exturls_api_url,
            headers=headers,
            # json={'url': url}
        )

        if response.status_code == 200:
            data = response.json()
            # results['raw'] = data
            results = data

        else:
            # append error to errors array
            msg = (
                f"Error fetching Wiki external urls data"
                f" Got {response.status_code} from {exturls_api_url}"
                f" Text: {response.text}"
            )

            from src import app
            app.logger.debug(msg)

            results.setdefault('errors', []).append(msg)  # create errors entry if not there and append msg

        return results


    if __name__ == "__main__":
        # Example command line test
        wiki = WikiUtils()
        test_url = "https://example.com"
        result = wiki.get_exturls(test_url)
        print(f"Test result for {test_url}:")
        print(result)
