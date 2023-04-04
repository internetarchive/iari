from unittest import TestCase

from pydantic import ValidationError

from src.models.api.enums import Lang
from src.models.api.job.article_job import ArticleJob
from src.models.wikimedia.enums import WikimediaDomain


class TestArticleJob(TestCase):
    def test_site(self):
        job = ArticleJob(title="", site="wikipedia")
        assert job.domain == WikimediaDomain.wikipedia

    def test_get_page_id(self):
        job = ArticleJob(title="Test", site="wikipedia.org", lang="en")
        job.get_page_id()
        assert job.page_id == 11089416

    def test_refresh(self):
        job = ArticleJob(title="Test", site="wikipedia", lang="en")
        assert job.refresh is False
        job = ArticleJob(title="Test", site="wikipedia", lang="en", refresh=True)
        assert job.refresh is True
        with self.assertRaises(ValidationError):
            ArticleJob(title="Test", site="wikipedia", lang="en", refresh="123")

    def test_extract_url_http(self):
        job = ArticleJob()
        job.url = "http://en.wikipedia.org/wiki/Test"
        job.extract_url()

        self.assertEqual(job.lang, Lang.en)
        self.assertEqual(job.domain, WikimediaDomain.wikipedia)
        self.assertEqual(job.title, "Test")

    def test_extract_url_https(self):
        job = ArticleJob()
        job.url = "https://en.wikipedia.org/wiki/Test"
        job.extract_url()

        self.assertEqual(job.lang, Lang.en)
        self.assertEqual(job.domain, WikimediaDomain.wikipedia)
        self.assertEqual(job.title, "Test")

    # noinspection PyStatementEffect
    def test_quoted_title(self):
        job = ArticleJob(
            url="https://en.wikipedia.org/wiki/GNU/Linux_naming_controversy"
        )
        job.extract_url()
        assert job.quoted_title == "GNU%2FLinux_naming_controversy"
