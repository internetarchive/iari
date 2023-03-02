from unittest import TestCase

from pydantic import ValidationError

from src.models.api.job.article_job import ArticleJob
from src.models.wikimedia.enums import WikimediaSite


class TestArticleJob(TestCase):
    def test_urldecode_title(self):
        job = ArticleJob(title="%20")
        job.urldecode_title()
        assert job.title == " "

    def test_site(self):
        job = ArticleJob(title="", site="wikipedia")
        assert job.site == WikimediaSite.wikipedia

    def test_get_page_id(self):
        job = ArticleJob(title="Test", site="wikipedia", lang="en")
        job.get_page_id()
        assert job.page_id == 11089416

    def test_refresh(self):
        job = ArticleJob(title="Test", site="wikipedia", lang="en")
        assert job.refresh is False
        job = ArticleJob(title="Test", site="wikipedia", lang="en", refresh=True)
        assert job.refresh is True
        with self.assertRaises(ValidationError):
            ArticleJob(title="Test", site="wikipedia", lang="en", refresh="123")
