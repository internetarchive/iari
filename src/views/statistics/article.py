from typing import Any, Tuple

from flask_restful import Resource, abort  # type: ignore

from src.models.exceptions import MissingInformationError
from src.models.wikimedia.enums import AnalyzerReturn
from src.views.statistics import StatisticsView


class Article(StatisticsView):
    """This models the get-statistics API
    It is instantiated at every request"""

    def __analyze_and_write_and_return__(self) -> Tuple[Any, int]:
        """Analyze, calculate the time, write statistics to disk and return it
        If we did not get statistics, return a meaningful error to the patron"""
        from src.models.api import app

        app.logger.info("__analyze_and_write_and_return__: running")
        if not self.wikipedia_analyzer:
            raise MissingInformationError("self.wikipedia_analyzer was None")
        self.__get_timing_and_statistics__()
        if self.wikipedia_analyzer.found:
            app.logger.debug("found article")
            if self.wikipedia_analyzer.is_redirect:
                app.logger.debug("found redirect")
                return AnalyzerReturn.IS_REDIRECT.value, 400
            else:
                app.logger.debug("adding time information and returning the statistics")
                self.__update_statistics_with_time_information__()
                # app.logger.debug(f"dictionary from analyzer: {self.statistics_dictionary}")
                # we got a json response
                # according to https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view
                # flask calls jsonify automatically
                self.__write_to_disk__()
                self.statistics_dictionary["served_from_cache"] = False
                # app.logger.debug("returning dictionary")
                return self.statistics_dictionary, 200
        else:
            return AnalyzerReturn.NOT_FOUND.value, 404

    def __handle_valid_job__(self):
        from src.models.api import app

        app.logger.debug("got valid job")
        if self.job.testing:
            return self.__setup_testing__()
        else:
            if not self.job.refresh:
                app.logger.info("trying to read from cache")
                self.__read_all_statistics_from_cache__()
                if (
                    self.statistics_dictionary
                    and not self.__more_than_2_days_old_cache__()
                ):
                    # We got the statistics from json, return them as is
                    app.logger.info(
                        f"Returning existing json from disk with date: {self.time_of_analysis}"
                    )
                    return self.statistics_dictionary, 200
            else:
                app.logger.info("got refresh from patron")
            # This will run if we did not return an analysis from disk yet
            self.__print_log_message_about_refresh__()
            self.__setup_wikipedia_analyzer__()
            return self.__analyze_and_write_and_return__()

    def __setup_testing__(self):
        from src.models.api import app

        app.logger.debug("testing...")
        self.__prepare_wikipedia_analyzer_if_testing__()
        if not self.wikipedia_analyzer:
            MissingInformationError("no self.wikipedia_analyzer")
        self.__get_timing_and_statistics__()
        # We set this to be able to test the refresh
        if self.job.refresh:
            self.statistics_dictionary["served_from_cache"] = False
            self.statistics_dictionary["refreshed_now"] = True
        else:
            self.statistics_dictionary["served_from_cache"] = True
            self.statistics_dictionary["refreshed_now"] = False
        return self.statistics_dictionary, 200
