import logging
from typing import Optional

from flask import request
from flask_restful import Resource, abort  # type: ignore

from src.helpers.console import console
from src.models.api.get_article_statistics.get_statistics_schema import (
    GetStatisticsSchema,
)
from src.models.api.job import Job
from src.models.wikimedia.enums import AnalyzerReturn, WikimediaSite
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    easter_island_short_tail_excerpt,
    easter_island_tail_excerpt,
    test_full_article,
)

logger = logging.getLogger(__name__)


class GetArticleStatistics(Resource):
    schema = GetStatisticsSchema()
    job: Optional[Job]

    def get(self):
        logger.debug("get: running")
        self.__validate_and_get_job__()
        if (
            self.job.lang.lower() == "en"
            and self.job.title
            and self.job.site == WikimediaSite.wikipedia
        ):
            from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer

            wikipedia_analyzer = None
            supported_test_titles = ["Test", "Easter Island"]
            if self.job.testing and self.job.title in supported_test_titles:
                if self.job.title == "Test":
                    logger.info(f"(testing) Analyzing {self.job.title} from test_data")
                    wikipedia_analyzer = WikipediaAnalyzer(
                        job=self.job, wikitext=test_full_article
                    )
                elif self.job.title == "Easter Island":
                    logger.info(f"(testing) Analyzing {self.job.title} from test_data")
                    wikipedia_analyzer = WikipediaAnalyzer(
                        job=self.job,
                        wikitext=f"{easter_island_head_excerpt}\n{easter_island_short_tail_excerpt}",
                    )
                else:
                    logger.warning(f"Ignoring unsupported test title {self.job.title}")
            if not wikipedia_analyzer:
                logger.info(f"Analyzing {self.job.title}...")
                # TODO use a work queue here like ReFill so
                #  we can easily scale the workload from thousands of users
                wikipedia_analyzer = WikipediaAnalyzer(job=self.job, check_urls=True)
            statistics = wikipedia_analyzer.get_statistics()
            if isinstance(statistics, dict):
                # we got a json response
                # according to https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view
                # flask calls jsonify automatically
                return statistics, 200
            elif statistics == AnalyzerReturn.NOT_FOUND:
                return statistics.value, 404
            elif statistics == AnalyzerReturn.IS_REDIRECT:
                return statistics.value, 400
            else:
                raise Exception("this should never be reached.")
        else:
            # Something was not valid, return a meaningful error
            logger.error("did not get what we need")
            if self.job.lang != "en":
                return "Only en language code is supported", 400
            if self.job.title == "":
                return "Title was missing", 400
            if self.job.site != "wikipedia":
                return "Only 'wikipedia' site is supported", 400

    def __validate_and_get_job__(self):
        """Helper method"""
        self.__validate__()
        self.__parse_into_job__()

    def __validate__(self):
        logger.debug("__validate__: running")
        errors = self.schema.validate(request.args)
        logger.debug(f"Found errors: {errors}")
        if errors:
            abort(400, error=str(errors))

    def __parse_into_job__(self):
        logger.debug("__parse_into_job__: running")
        logger.debug(request.args)
        self.job = self.schema.load(request.args)
        console.print(self.job.dict())
