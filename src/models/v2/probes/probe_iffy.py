import json
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional
from urllib.parse import urlparse

from src.models.v2.probes.iari_probe import IariProbeBase
from src.constants.constants import ProbeMethod


def get_top_domain(url):
    # Ensure URL has a scheme so urlparse can work correctly
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    netloc = urlparse(url).netloc
    parts = netloc.split('.')

    if len(parts) >= 3:
        # Take the last 3 parts (e.g., 'a.b.com')
        return '.'.join(parts[-3:])
    else:
        # Just return the full domain
        return netloc


class ProbeIffy(IariProbeBase):  # we should define a return type here
    """
    "Implements" IariProbeBase class
    """

    # json_data = Optional[Dict[str, Any]] = None
    # iffy_dict = None
    iffy_dict: ClassVar[Dict[str, Any]] = {}  # dict of entries should be persistent

    # probe_name = ProbeMethod.TEST.value
    @property
    def probe_name(self):
        return ProbeMethod.IFFY.value

    @staticmethod
    def probe(url):
        """
        returns results of iffy probe for url
        """
        now = datetime.utcnow()
        results = {
            "url": url,
            "timestamp": datetime.timestamp(now),
            "isodate": now.isoformat(),
        }

        try:
            results.update(ProbeIffy().probe_assess(url))

        except Exception as e:
            # raise Exception(f"Unknown error while probing {url} with {ProbeIffy().probe_name}. args: {e.args}")
            raise Exception(f"Unknown error while probing {url} with {ProbeIffy().probe_name}: {str(e)}")

        return results

    @classmethod
    def ensure_resources(cls):
        from src import app

        # load json_data if not loaded already
        if not ProbeIffy.iffy_dict:
            app.logger.debug(f"Regenerating Iffy Dict")
            json_path = "external_data/iffy/iffy-news.json"
            try:
                app.logger.debug(f"LOADING iffy dict from {json_path}")

                with open(json_path, 'r') as f:
                    json_data = json.load(f)
                    # use dictionary comprehension to convert
                    ProbeIffy.iffy_dict = {
                        entry["Domain"]: {"score": entry["Score"]}
                        for entry in json_data}

            except (FileNotFoundError, json.JSONDecodeError) as e:
                app.logger.debug(f"Error loading iffy JSON from {json_path}: {e}")
                ProbeIffy.iffy_dict = {}  # fallback to empty dict


    @staticmethod
    def probe_assess(url):

        ProbeIffy.ensure_resources()

        from src import app
        # app.logger.debug(f"iffy dict LOADED, getting top domain")
        # app.logger.debug(f"iffy dict size: {len(ProbeIffy.iffy_dict)}")


        # get top domain from url
        tld = get_top_domain(url)

        # get keyed entry from iffy data (or undefined)
        if tld in ProbeIffy.iffy_dict:
            data = {
                "score": ProbeIffy.iffy_dict[tld]["score"]
            }
        else:
            data = ""

        now = datetime.utcnow()
        results = {
            "url": url,
            "timestamp": datetime.timestamp(now),
            "isodate": now.isoformat(),
            "raw": data
        }

        if not data:
            results.update({
                "nodata": True
            })

        return results
