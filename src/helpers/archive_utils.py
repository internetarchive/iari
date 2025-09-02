# probe_utils.py
from typing import Optional, Union

from src.helpers.cache_utils import get_cache, set_cache, is_cached, CacheType

from src.constants.constants import ProbeMethod
from src.models.v2.probes.probe_test import ProbeTest
from src.models.v2.probes.probe_trust_project import ProbeTrustProject
from src.models.v2.probes.probe_verifyi import ProbeVerifyi

BASE_WAYBACK_CDX_URL = "https://web.archive.org/cdx/search/cdx"


class ArchiveUtils:

    @staticmethod
    def _get_response(self, url, params):
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            app.logger.error(f"Request failed: {e}.")
            # print(f"Request failed (attempt {retries}/{self.max_retries}): {e}. Retrying in {wait_time:.2f}s...")
            return {
                errors: [
                    f"Wayback API Request failed: {e}"
                ]
            }
        # return None


    @staticmethod
    def get_all_snapshots(self, url, from_year=None, to_year=None, limit=None, only_status_200=True):
        params = {
            "url": url,
            "output": "json",
            "fl": "timestamp,original,statuscode"
        }
        if from_year:
            params["from"] = from_year
        if to_year:
            params["to"] = to_year
        if limit:
            params["limit"] = limit
        if only_status_200:
            params["filter"] = "statuscode:200"

        data = self._get_response(self.BASE_WAYBACK_CDX_URL, params)

        # if data["errors"] ....

        if not data or len(data) < 2:
            return []

        snapshots = []
        for row in data[1:]:
            snapshots.append({
                "timestamp": row[0],
                "url": f"{self.BASE_ARCHIVE_URL}/{row[0]}/{row[1]}",
                "statuscode": row[2]
            })
        return snapshots
