# from unittest import TestCase
#
# from marshmallow import ValidationError
#
#
#
# class TestGetUrlsSchema(TestCase):
#     def test_return_object_valid(self):
#         from src.models.api.statistics import (
#             GetUrlsSchema,
#         )
#         from src.models.api.job import Job
#
#         gss = GetUrlsSchema()
#         job = gss.load(
#             dict(
#                 title="test",
#                 refresh=True,
#                 lang="en",
#                 site="wikipedia",
#                 subset="not_found",
#             )
#         )
#         assert job == Job(title="test", refresh=True, subset=Subset.not_found)
#         gss = GetUrlsSchema()
#         job = gss.load(
#             dict(
#                 title="test", refresh=1, lang="en", site="wikipedia", subset="malformed"
#             )
#         )
#         assert job == Job(title="test", refresh=True, subset=Subset.malformed)
#         gss = GetUrlsSchema()
#         job = gss.load(dict(title="test", refresh="true", lang="en", site="wikipedia"))
#         assert job == Job(title="test", refresh=True)
#
#     def test_invalid_subset(self):
#         from src.models.api.statistics import (
#             GetUrlsSchema,
#         )
#
#         gss = GetUrlsSchema()
#         with self.assertRaises(ValidationError):
#             gss.load(
#                 dict(
#                     title="test",
#                     refresh=True,
#                     lang="en",
#                     site="wikipedia",
#                     subset="not_found3332323",
#                 )
#             )
