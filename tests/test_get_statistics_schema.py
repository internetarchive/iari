from unittest import TestCase

from marshmallow import ValidationError

from src.models.api.job import Job
from src.models.api.job.article_job import ArticleJob
from src.models.api.statistics.article.article_schema import ArticleSchema


class TestArticleSchema(TestCase):
    """This tests the get-statistics API schema"""

    def test_return_object_valid(self):
        gss = ArticleSchema()
        job = gss.load(dict(title="test", refresh=True, lang="en", site="wikipedia"))
        assert job == ArticleJob(title="test", refresh=True)
        gss = ArticleSchema()
        job = gss.load(dict(title="test", refresh=1, lang="en", site="wikipedia"))
        assert job == ArticleJob(title="test", refresh=True)
        gss = ArticleSchema()
        job = gss.load(dict(title="test", refresh="true", lang="en", site="wikipedia"))
        assert job == ArticleJob(title="test", refresh=True)

    def test_return_object_invalid(self):
        gss = ArticleSchema()
        with self.assertRaises(ValidationError):
            gss.load(dict(title="test", refresh=11, lang="en", site="wikipedia"))

    # def test_validate_invalid_title(self):
    #     gss = ArticleSchema()
    #     errors = gss.validate(
    #         dict(
    #             # title="test",
    #             refresh=True,
    #             lang="en",
    #             site="wikipedia",
    #         )
    #     )
    #     assert errors == {"title": ["Missing data for required field."]}

    def test_validate_invalid_refresh(self):
        gss = ArticleSchema()
        errors = gss.validate(
            dict(title="test", refresh="truest", lang="en", site="wikipedia")
        )
        assert errors == {"refresh": ["Not a valid boolean."]}

    def test_validate_invalid_lang(self):
        gss = ArticleSchema()
        errors = gss.validate(
            dict(title="test", refresh=True, lang="enen", site="wikipedia")
        )
        assert errors == {"lang": ["Must be one of: en."]}

    def test_validate_invalid_site(self):
        gss = ArticleSchema()
        errors = gss.validate(
            dict(title="test", refresh=True, lang="enen", site="wikipediaaaaaaaaaa")
        )
        assert errors == {
            "lang": ["Must be one of: en."],
            "site": ["Must be one of: wikipedia."],
        }
