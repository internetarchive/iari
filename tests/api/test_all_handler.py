from src.models.api.job.article_job import ArticleJob
from src.models.api.statistics.all import AllHandler


class TestAllHandler:
    def test_fetch_and_compile(self):
        handler = AllHandler(job=ArticleJob(title="SNCASO"))
        handler.fetch_and_compile()
        assert handler.data != {}
        assert len(handler.references) == 30
        assert handler.compilation != {}
