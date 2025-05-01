# probe_utils.py
from typing import Optional, Union

from src.helpers.cache_utils import get_cache, set_cache, is_cached, CacheType

from src.constants.constants import ProbeMethod
from src.models.v2.probes.probe_test import ProbeTest
from src.models.v2.probes.probe_trust_project import ProbeTrustProject
from src.models.v2.probes.probe_verifyi import ProbeVerifyi


class ProbeUtils:
    @staticmethod
    def run_probe_logic(data):
        # complex logic here
        return {"result": "ok"}



    @staticmethod
    def get_probe_results(url_link: str, probe_list: list, refresh: bool = False):
        """
        returns overall truth score and probe results for url_link for each probe in probe_list
        returns { score: <xxx>, probe_results{ a: <xxx>, b: <xxx>, c: <xxx> }

        TODO: error if probe list empty? or not...

        """

        from src import app
        app.logger.debug(f"==> get_probe_results: url_link: {url_link}, probe_list: {probe_list}, refresh = {str(refresh)}")

        probe_results = {}

        if refresh:
            """
            if refresh:
                (fetch all probes anew, and save new data in cache for url and probe)
                for p in probe_list
                    fetch p(url)
                    save in cache p-url
            """

            # fetch all probes anew, and save new data in cache for url/probe combo
            for p in probe_list:
                new_data = ProbeUtils.get_probe_data(url_link, p)
                probe_results[p] = new_data

                # TODO NB what to do if new_data is error?
                #   may want to keep cache as is if already there,
                #   and "send back" error as response
                #   basically, not save to cache if error

                # TODO have some way of tagging probe data with a timestamp of access date

                set_cache(url_link, CacheType.probes, p, new_data)

        else:
            """
            if not refresh:
                for p in probe_list
                    if is_cached, do nothing, as cache already exists fpr p-url
                    if not is_cached
                        fetch p(url)
                        set_cache p-url
            """
            for p in probe_list:
                if not is_cached(url_link, CacheType.probes, p):
                    new_data = ProbeUtils.get_probe_data(url_link, p)
                    probe_results[p] = new_data

                    # TODO NB what to do if new_data is error?
                    #
                    # do not save errors in cache!
                    #
                    # IDEA: set_cache can behave like a "store another snapshot". This will give us a way
                    #   to have a sort of database of cached fetches, to have a hotory
                    #   we probably should have a comparison so we dont resave same data, but should
                    #   at least save a "snapshot" date if multiple fetches produce same results

                    set_cache(url_link, CacheType.probes, p, new_data)

                else:  # data for probe p is cached, so use it
                    new_data = get_cache(url_link, CacheType.probes, p)
                    probe_results[p] = new_data

        # # gather all cached probe results into probe_results, regardless of refresh status
        # """
        # in either case of refresh:
        #     gather all probes from cache
        #     calc score
        #     return: { score:<xxx>, probe_results{ a: <xxx>, b: <xxx>, c: <xxx> }
        # """
        # for p in probe_list:
        #     data = get_cache(url_link, CacheType.probes, p)
        #     probe_results[p] = data

        score = ProbeUtils.get_probe_score(probe_results)

        return {
            "score": score,
            "probes": probe_results
        }


    @staticmethod
    def get_probe_data(url, probe_name):
        """
        fetch data from probe for specified url

        TODO may want to always save to cache here
        """

        results = {}

        # try all the probes we have
        try:
            # TEST method
            if probe_name.upper() == ProbeMethod.TEST.value:
                results = ProbeTest.probe(url=url)

            # VERIFYI method
            elif probe_name.upper() == ProbeMethod.VERIFYI.value:
                results = ProbeVerifyi.probe(url=url)

            # TRUST_PROJECT method
            elif probe_name.upper() == ProbeMethod.TRUST_PROJECT.value:
                results = ProbeTrustProject.probe(url=url)

            # probe method not supported
            else:
                results = {
                    "errors": [
                        f"Unknown probe: {probe_name}"
                    ]
                }

        except Exception as e:
            results[probe_name] = {
                "errors": [
                    f"Error while probing {probe_name} ({str(e)})."
                ]
            }

        return results


    @staticmethod
    def get_probe_score(probe_results) -> Optional[int]:
        """
        returns a single metric based on evaluation of probe_results

        TODO: probe evaluation to be determined
        """
        score = 0
        for probe_key, probe_value in probe_results.items():

            # must update score variable based on evaluation
            # of probe_value, which is specific to each probe_key.
            # similar switching as in __get_probe_data__
            #
            # adjust score accordingly
            pass

        return score

