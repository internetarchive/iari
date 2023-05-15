from src.v2.models.api.handlers.all import AllHandler
from src.v2.models.api.job.article_job import ArticleJob
from src.v2.models.api.schema.article_schema import ArticleSchema
from src.v2.views.statistics import StatisticsView


class All(StatisticsView):
    """This models the get-statistics API
    It is instantiated at every request"""

    def __setup_io__(self):
        pass

    schema = ArticleSchema()
    job: ArticleJob

    def get(self):
        self.__validate_and_get_job__()
        handler = AllHandler(job=self.job)
        handler.fetch_and_compile()
        return handler.compilation, 200
