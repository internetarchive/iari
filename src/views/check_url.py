from typing import Any, Tuple, Dict

from flask import request
from flask_restful import Resource, abort  # type: ignore
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    easter_island_short_tail_excerpt,
    easter_island_tail_excerpt,
    electrical_breakdown_full_article,
    test_full_article,
)

from src import console
from src.models.api.check_url.check_url_schema import CheckUrlSchema
from src.models.api.check_url.statistics import CheckUrlStatistics
from src.models.api.job.check_url_job import CheckUrlJob


class CheckUrl(Resource):
    """
    This models all action based on requests from the frontend/patron
    It is instantiated at every request

    This view does not contain any of the checking logic.
    See src/models/checking
    """

    check_url_job: CheckUrlJob
    schema: CheckUrlSchema()
    serving_from_json: bool = False
    headers: Dict[str, Any] = {
        "Access-Control-Allow-Origin": "*",
    }
    data: Dict[str, Any] = {}

    def get(self):
        """This is the main method and the entrypoint for flask
        Every branch in this method has to return a tuple (Any,response_code)"""
        from src.models.api import app

        app.logger.debug("get: running")
        # todo verify we got a url and a timeout
        self.__validate_and_get_url__()
        # we default to 2 second timeout

    def __validate_and_get_url__(self):
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
        self.check_url_job = self.schema.load(request.args)
        # We print the job
        console.print(self.check_url_job.dict())

    def __update_and_write_to_disk__(self) -> None:
        """Helper method"""
        from src.models.api import app

        app.logger.info("__analyze_and_write_and_return__: running")
        app.logger.debug("found article")
        app.logger.debug("adding time information and returning the statistics")
        # self.__update_statistics_with_time_information__()
        # we got a json response
        # according to https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view
        # self.__write_to_disk__()
        # self.statistics_dictionary["served_from_cache"] = False

    def return_data(self) -> Tuple[Dict[str, Any], int, Dict[str, Any]]:
        # todo rewrite
        from src.models.api import app

        app.logger.debug("return_data: running")
        return (
            CheckUrlStatistics(
                # url_details=self.url_details,
                # urls=self.urls,
                served_from_cache=self.serving_from_json,
                refreshed_now=not self.serving_from_json,
            ).dict(),
            200,
            # https://stackoverflow.com/a/68843172
            self.headers,
        )

    def __extract_urls_from_json__(self):
        """Extract WikipediaUrls from the json depending on what subset the patron asked for"""
        raise NotImplementedError()
        # from src.models.api import app
        #
        # app.logger.debug("__extract_urls_from_json__: running")
        # # check if the json exists by
        # if exists(f"json/urls/")
        # if (
        #     self.statistics_dictionary
        #     and "references" in self.statistics_dictionary.keys()
        #     and self.statistics_dictionary["references"] is not None
        # ):
        #     self.urls = self.statistics_dictionary["references"]["urls"]
        #     app.logger.debug(f"found urls {self.urls}")
        #     references: List[ReferenceStatistic] = self.statistics_dictionary[
        #         "references"
        #     ]["details"]
        #     for reference in references:
        #         app.logger.debug(f"Working on {reference}")
        #         urls_details = reference["urls"]
        #         if urls_details:
        #             app.logger.debug(
        #                 f"Found url details {urls_details} with {len(urls_details)} url objects"
        #             )
        #             for url in urls_details:
        #                 url_object = WikipediaUrl(**url)
        #                 if self.job.subset:
        #                     if self.job.subset == Subset.not_found:
        #                         if url_object.status_code == 404:
        #                             self.url_details.append(url_object)
        #                     if self.job.subset == Subset.malformed:
        #                         if url_object.malformed_url:
        #                             self.url_details.append(url_object)
        #                 else:
        #                     self.url_details.append(url_object)
        #     app.logger.info(f"found {len(self.url_details)} url objects")
        # else:
        #     app.logger.warning("no references in self.statistics_dictionary")
