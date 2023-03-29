from src.models.api.all import AllHandler
from src.models.api.job.article_job import ArticleJob


class TestAllHandler:
    def test_fetch_and_compile_sncaso(self):
        handler = AllHandler(job=ArticleJob(url="https://en.wikipedia.org/wiki/SNCASO"))
        handler.fetch_and_compile()
        assert handler.data != {}
        assert len(handler.references) == 45
        assert handler.compilation != {}
        assert len(handler.compilation["url_details"]) == 10
        assert len(handler.compilation["doi_details"]) == 0

    # DISABLED because check-url bug causes return of non json which is terrible
    # def test_fetch_and_compile_bicycle(self):
    #     handler = AllHandler(job=ArticleJob(title="Bicycle"))
    #     handler.fetch_and_compile()
    #     assert handler.data != {}
    #     assert len(handler.references) == 0
    #     assert handler.compilation != {}
    #     assert len(handler.compilation["url_details"]) == 0
    #     assert len(handler.compilation["doi_details"]) == 0

    def test___fetch_doi_details__(self):
        handler = AllHandler(
            job=ArticleJob(url="https://en.wikipedia.org/wiki/Bicycle")
        )
        handler.__fetch_article__()
        assert handler.error is False
        assert handler.data != {}
        # exit()
        handler.__fetch_references__()
        handler.__fetch_doi_details__()
        assert handler.dois != set()
        assert len(handler.doi_details) == 7

    def test_number_of_dois(self):
        handler = AllHandler(
            job=ArticleJob(url="https://en.wikipedia.org/wiki/Bicycle")
        )
        handler.__fetch_article__()
        handler.__fetch_references__()
        assert handler.number_of_dois == 7
