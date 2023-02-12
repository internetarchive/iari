from typing import Any, List, Optional, Tuple

from flask_restful import Resource, abort  # type: ignore

from src.models.api.enums import Subset
from src.models.api.get_statistics.get_statistics import GetStatistics
from src.models.api.get_statistics.get_url_statistics.get_urls_schema import (
    GetUrlsSchema,
)
from src.models.api.get_statistics.get_url_statistics.url_statistics import (
    UrlStatistics,
)
from src.models.api.get_statistics.references import ReferenceStatistics, Urls
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.enums import AnalyzerReturn
from src.models.wikimedia.wikipedia.url import WikipediaUrl
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    easter_island_short_tail_excerpt,
    easter_island_tail_excerpt,
    electrical_breakdown_full_article,
    test_full_article,
)


class GetUrlStatistics(GetStatistics):
    """This models the get-statistics API
    It is instantiated at every request"""

    url_details: List[WikipediaUrl] = []
    urls: Urls = Urls()
    schema = GetUrlsSchema()

    def __update_and_write_to_disk__(self) -> None:
        """Helper method"""
        from src.models.api import app

        app.logger.info("__analyze_and_write_and_return__: running")
        app.logger.debug("found article")
        app.logger.debug("adding time information and returning the get_statistics")
        self.__update_statistics_with_time_information__()
        # app.logger.debug(f"dictionary from analyzer: {self.statistics_dictionary}")
        # we got a json response
        # according to https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view
        # flask calls jsonify automatically
        self.__write_to_disk__()
        self.statistics_dictionary["served_from_cache"] = False
        self.statistics_dictionary["refreshed_now"] = True

    def __handle_valid_job__(self):
        from src.models.api import app

        app.logger.debug("got valid job")
        if self.job.testing:
            self.__setup_testing__()
        else:
            if not self.job.refresh:
                app.logger.info("trying to read from cache")
                self.__read_all_statistics_from_cache__()
                if (
                    self.statistics_dictionary
                    and not self.__more_than_2_days_old_cache__()
                ):
                    # We got the get_statistics from json
                    self.serving_from_json = True
                    app.logger.info(
                        f"Returning existing json from disk with date: {self.time_of_analysis}"
                    )
                    return self.return_a_subset()
                else:
                    # data too old or not found
                    pass
            else:
                app.logger.info("got refresh from user")
            # Refresh
            self.__print_log_message_about_refresh__()
            self.__setup_wikipedia_analyzer__()
            self.__get_timing_and_statistics__()
            # Check if not found or redirect
            if not self.wikipedia_analyzer.found:
                return AnalyzerReturn.NOT_FOUND.value, 404
            if self.wikipedia_analyzer.is_redirect:
                app.logger.debug("found redirect")
                return AnalyzerReturn.IS_REDIRECT.value, 400
            self.__update_and_write_to_disk__()
        # Always return here no matter whether testing or not
        return self.return_a_subset()

    def return_a_subset(self) -> Tuple[Any, int]:
        from src.models.api import app

        app.logger.debug("return_a_subset: running")
        if self.job and self.job.subset:
            from src.models.api import app

            app.logger.debug("got subset")
            if self.job.subset == Subset.not_found:
                app.logger.debug("got not found")
            elif self.job.subset == Subset.malformed:
                app.logger.debug("got malformed")
        self.__extract_urls_from_json__()
        # We return no matter what but with an empty list and agg=None if no urls were found
        return (
            UrlStatistics(
                url_details=self.url_details,
                urls=self.urls,
                served_from_cache=self.serving_from_json,
                refreshed_now=not self.serving_from_json,
                isodate=self.statistics_dictionary["isodate"],
                timing=self.statistics_dictionary["timing"],
                timestamp=self.statistics_dictionary["timestamp"],
                title=self.statistics_dictionary["title"],
                page_id=self.statistics_dictionary["page_id"],
                site=self.statistics_dictionary["site"],
                lang=self.statistics_dictionary["lang"],
            ).dict(),
            200,
        )

    def __extract_urls_from_json__(self):
        """Extract WikipediaUrls from the json depending on what subset the patron asked for"""
        from src.models.api import app

        app.logger.debug("__extract_urls_from_json__: running")
        if (
            self.statistics_dictionary
            and "references" in self.statistics_dictionary.keys()
            and self.statistics_dictionary["references"] is not None
        ):
            self.urls = self.statistics_dictionary["references"]["urls"]
            app.logger.debug(f"found urls {self.urls}")
            references: List[ReferenceStatistics] = self.statistics_dictionary[
                "references"
            ]["details"]
            for reference in references:
                app.logger.debug(f"Working on {reference}")
                urls_details = reference["urls"]
                if urls_details:
                    app.logger.debug(
                        f"Found url details {urls_details} with {len(urls_details)} url objects"
                    )
                    for url in urls_details:
                        url_object = WikipediaUrl(**url)
                        if self.job.subset:
                            if self.job.subset == Subset.not_found and url_object.status_code == 404:
                                self.url_details.append(url_object)
                            if self.job.subset == Subset.malformed and url_object.malformed_url:
                                self.url_details.append(url_object)
                        else:
                            self.url_details.append(url_object)
            app.logger.info(f"found {len(self.url_details)} url objects")
        else:
            app.logger.warning("no references in self.statistics_dictionary")

    def __setup_testing__(self) -> None:
        from src.models.api import app

        app.logger.debug("testing...")
        self.__prepare_wikipedia_analyzer_if_testing__()
        if not self.wikipedia_analyzer:
            MissingInformationError("no self.wikipedia_analyzer")
        self.__get_timing_and_statistics__()
        # We set this to be able to test the refresh
        if not self.job:
            raise MissingInformationError()
        if self.job.refresh:
            self.statistics_dictionary["served_from_cache"] = False
            self.statistics_dictionary["refreshed_now"] = True
        else:
            self.statistics_dictionary["served_from_cache"] = True
            self.statistics_dictionary["refreshed_now"] = False
