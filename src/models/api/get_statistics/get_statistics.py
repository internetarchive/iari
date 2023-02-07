import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from flask import request
from flask_restful import Resource, abort  # type: ignore

from src import WikimediaSite, console
from src.models.api.get_statistics.get_statistics_schema import GetStatisticsSchema
from src.models.api.job import Job
from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo
from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    easter_island_short_tail_excerpt,
    easter_island_tail_excerpt,
    electrical_breakdown_full_article,
    test_full_article,
)


class GetStatistics(Resource):
    """Abstract class modeling a get-statistics endpoint"""

    schema = GetStatisticsSchema()
    job: Optional[Job]
    wikipedia_analyzer: Optional[WikipediaAnalyzer] = None
    statistics_dictionary: Dict[str, Any] = {}
    time_of_analysis: Optional[datetime] = None
    two_days_ago = datetime.utcnow() - timedelta(hours=48)
    serving_from_json: bool = False

    def __validate_and_get_job__(self):
        """Helper method"""
        self.__validate__()
        self.__parse_into_job__()

    def __validate__(self):
        from src.models.api import app

        app.logger.debug("__validate__: running")
        errors = self.schema.validate(request.args)
        if errors:
            app.logger.debug(f"Found errors: {errors}")
            abort(400, error=str(errors))

    def __parse_into_job__(self):
        from src.models.api import app

        app.logger.debug("__parse_into_job__: running")
        # app.logger.debug(request.args)
        self.job = self.schema.load(request.args)
        console.print(self.job.dict())

    def __more_than_2_days_old_cache__(self) -> bool:
        """This reads from the cache and returns a boolean"""
        from src.models.api import app

        app.logger.debug("__not_more_than_2_days_old_cache__: running")
        if not self.statistics_dictionary:
            self.__read_all_statistics_from_cache__()
        if self.statistics_dictionary:
            self.__convert_analysis_timestamp__()
            if not self.time_of_analysis:
                raise MissingInformationError("self.time_of_analysis was None")
            if self.time_of_analysis < self.two_days_ago:
                app.logger.debug("more than 48h ago")
                return True
            else:
                app.logger.debug("not more than 48h ago")
        # Default to False ie. also return false when no json on disk
        return False

    def __read_all_statistics_from_cache__(self):
        io = FileIo(job=self.job)
        io.read_from_disk()
        if io.statistics_dictionary:
            self.statistics_dictionary = io.statistics_dictionary

    def __analyze_and_write_and_return__(self) -> Tuple[Any, int]:
        """Analyze, calculate the time, write get_statistics to disk and return it
        If we did not get get_statistics, return a meaningful error to the user"""
        pass

    def __prepare_wikipedia_analyzer_if_testing__(self):
        from src.models.api import app

        app.logger.debug("__prepare_wikipedia_analyzer_if_testing__: running")
        supported_test_titles = ["Test", "Easter Island", "Electrical breakdown"]
        if self.job.testing and self.job.title in supported_test_titles:
            if self.job.title == "Test":
                app.logger.info(f"(testing) Analyzing {self.job.title} from test_data")
                self.wikipedia_analyzer = WikipediaAnalyzer(
                    job=self.job, wikitext=test_full_article
                )
            elif self.job.title == "Electrical_breakdown":
                app.logger.info(f"(testing) Analyzing {self.job.title} from test_data")
                self.wikipedia_analyzer = WikipediaAnalyzer(
                    job=self.job,
                    wikitext=electrical_breakdown_full_article,
                    check_urls=True,
                )
            elif self.job.title == "Easter Island":
                app.logger.info(f"(testing) Analyzing {self.job.title} from test_data")
                self.wikipedia_analyzer = WikipediaAnalyzer(
                    job=self.job,
                    wikitext=f"{easter_island_head_excerpt}\n{easter_island_short_tail_excerpt}",
                )
            else:
                app.logger.warning(f"Ignoring unsupported test title {self.job.title}")

    def __get_timing_and_statistics__(self):
        from src.models.api import app

        app.logger.debug("__get_timing_and_statistics__: running")
        if not self.wikipedia_analyzer:
            raise MissingInformationError("self.wikipedia_analyzer was None")
        # https://realpython.com/python-timer/
        start_time = time.perf_counter()
        self.statistics_dictionary = self.wikipedia_analyzer.get_statistics()
        # app.logger.debug(f"self.wikipedia_analyzer.found:{self.wikipedia_analyzer.found}")
        end_time = time.perf_counter()
        self.timing = round(float(end_time - start_time), 3)

    def __update_statistics_with_time_information__(self):
        """Update the dictionary before returning it"""
        if self.statistics_dictionary:
            self.statistics_dictionary["timing"] = self.timing
            timestamp = datetime.timestamp(datetime.utcnow())
            self.statistics_dictionary["timestamp"] = int(timestamp)
            isodate = datetime.isoformat(datetime.utcnow())
            self.statistics_dictionary["isodate"] = str(isodate)
        else:
            raise ValueError("not a dict")

    def __write_to_disk__(self):
        io = FileIo(job=self.job, statistics_dictionary=self.statistics_dictionary)
        io.write_to_disk()

    def __print_log_message_about_refresh__(self):
        from src.models.api import app

        if self.job.refresh:
            app.logger.info("got force refresh from user")
        else:
            app.logger.info("we may have the data but it is too old, refreshing...")

    def __convert_analysis_timestamp__(self):
        from src.models.api import app

        app.logger.debug(f"two days ago {self.two_days_ago}")
        self.time_of_analysis = datetime.fromtimestamp(
            self.statistics_dictionary["timestamp"]
        )
        app.logger.debug(f"analysis time {self.time_of_analysis}")

    def __handle_valid_job__(self):
        """This is the main work horse"""
        pass

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

    def __return_meaningful_error__(self):
        from src.models.api import app

        app.logger.error("__return_meaningful_error__: running")
        if self.job.lang != "en":
            return "Only language code 'en' is supported, currently", 400
        if self.job.title == "":
            return "Title was missing", 400
        if self.job.site != "wikipedia":
            return "Only 'wikipedia' site is supported", 400

    def __setup_wikipedia_analyzer__(self):
        if not self.wikipedia_analyzer:
            from src.models.api import app

            app.logger.info(f"Analyzing {self.job.title}...")
            self.wikipedia_analyzer = WikipediaAnalyzer(job=self.job, check_urls=True)

    def get(self):
        """This is the main method and the entrypoint for flask
        Every branch in this method has to return a tuple (Any,response_code)"""
        from src.models.api import app

        app.logger.debug("get: running")
        self.__validate_and_get_job__()
        if (
            self.job.lang.value == "en"
            and self.job.title
            and self.job.site == WikimediaSite.wikipedia
        ):
            return self.__handle_valid_job__()
        else:
            return self.__return_meaningful_error__()
