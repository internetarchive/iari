from unittest import TestCase

from marshmallow import ValidationError

from src.models.api.job.article_job import ArticleJob
from src.models.api.schema.article_schema import ArticleSchema
from src.models.wikimedia.enums import WikimediaDomain


class TestArticleSchema(TestCase):
    """This tests the get-statistics API schema"""

    def test_return_object_valid(self):
        gss = ArticleSchema()
        job = gss.load(
            dict(
                url="https://en.wikipedia.org/wiki/Easter_Island",
                refresh=True,
                regex="test",
            )
        )
        assert job == ArticleJob(
            url="https://en.wikipedia.org/wiki/Easter_Island",
            refresh=True,
            title="Easter_Island",
            lang="en",
            site=WikimediaDomain.wikipedia,
            regex="test",
        )

    def test_return_object_invalid(self):
        gss = ArticleSchema()
        with self.assertRaises(ValidationError):
            gss.load(
                dict(
                    url="https://en.wikipedia.org/wiki/Easter_Island",
                    refresh=11,
                    regex="test",
                )
            )

    def test_validate_invalid_refresh(self):
        gss = ArticleSchema()
        errors = gss.validate(
            dict(
                url="https://en.wikipedia.org/wiki/Easter_Island",
                refresh="truest",
                regex="test",
            )
        )
        assert errors == {"refresh": ["Not a valid boolean."]}
