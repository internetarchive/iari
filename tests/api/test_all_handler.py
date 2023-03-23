from src.models.api.all import AllHandler
from src.models.api.job.article_job import ArticleJob


class TestAllHandler:
    def test_fetch_and_compile_sncaso(self):
        handler = AllHandler(job=ArticleJob(title="SNCASO"))
        handler.fetch_and_compile()
        assert handler.data != {}
        assert len(handler.references) == 30
        assert handler.compilation != {}
        assert len(handler.compilation["url_details"]) == 8
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
        handler = AllHandler(job=ArticleJob(title="Bicycle"))
        handler.__fetch_article__()
        handler.__fetch_references__()
        handler.__fetch_doi_details__()
        assert handler.dois == {
            "10.1177/03635465030310041801",
            "10.1016/0015-0568(81)90023-3",
            "10.3141/2143-20",
            "10.1098/rspa.2007.1857",
            "10.1119/1.19504",
            "10.1007/s11524-010-9509-6",
            "10.3141/2247-05",
        }
        assert len(handler.doi_details) == 7

    def test_number_of_dois(self):
        handler = AllHandler(job=ArticleJob(title="Bicycle"))
        handler.__fetch_article__()
        handler.__fetch_references__()
        assert handler.number_of_dois == 7
