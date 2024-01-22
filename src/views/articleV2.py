# from flask_restful import Resource, abort  # type: ignore
# from marshmallow import Schema

from src.models.job.articleV2_job import ArticleV2Job
from src.models.schema.articleV2_schema import ArticleV2Schema
from src.views.statistics.write_view import StatisticsWriteView
from src.models.wikimedia.enums import AnalyzerReturn, WikimediaDomain


# NB using ArticleV2 as object name to avoid conflict with legacy Article object
class ArticleV2(StatisticsWriteView):
    """
    returns data associated with article specified by the schema
    """

    schema = ArticleV2Schema()
    job: ArticleV2Job

    def __setup_io__(self):
        """
        implementation for StatisticsWriteView.__setup_io__
        """
        self.io = ArticleV2FileIo(job=self.job)

    def __return_article_data__(self):
        from src import app
        app.logger.debug("got valid job")

        self.__setup_and_read_from_cache__()  # from inherited StatisticsWriteView

        if self.io.data and not self.job.refresh:
            # we have cached data - return it, if not force refresh

            app.logger.info("Returning articleV2 data from cache")

            self.__setup_and_read_from_cache__()
            if self.io.data:
                # We got the statistics from json, return them as is
                app.logger.info(
                    f"Returning existing json from disk with date: {self.time_of_analysis}"
                )
                return self.io.data, 200
        else:
            # we have to regenerate cache from scratch
            app.logger.info("got refresh from patron or no data in cache")
            self.__print_log_message_about_refresh__()
            self.__setup_wikipedia_analyzer__()
            return self.__analyze_and_write_and_return__()

    def get(self):
        """
        main entrypoint for flask
        must return a tuple (Any,response_code)
        """
        from src import app
        app.logger.debug("statistics/article/get: running")

        self.__validate_and_get_job__()  # generic for all endpoints
        if (
            self.job.lang == "en"
            and self.job.title
            and self.job.domain == WikimediaDomain.wikipedia
        ) or self.job.url:
            return self.__return_article_data__()
        else:
            return self.__return_article_error__()

    def __return_article_error__(self):
        from src import app
        if self.job.title == "":
            app.logger.error("ArticleV2: ERROR: Title is missing")
            return "Title is missing", 400
        if self.job.domain != "wikipedia":
            app.logger.error("ArticleV2: ERROR: Only 'wikipedia' site is supported")
            return "Only 'wikipedia' site is supported", 400


    # def __write_article_to_disk__(self):
    #     article_io = ArticleV2FileIo(
    #         job=self.job,
    #         data=self.io.data,
    #         iari_id=self.job.iari_id,
    #     )
    #     article_io.write_to_disk()
    #
    # def __write_references_to_disk__(self):
    #     references_file_io = ReferencesFileIo(
    #         references=self.wikipedia_analyzer.reference_statistics
    #     )
    #     references_file_io.write_references_to_disk()
