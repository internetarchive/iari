from pprint import pprint
from unittest import TestCase

from marshmallow import Schema, fields, ValidationError

from src import console
from src.models.wikimedia.wikipedia.templates.english_wikipedia_page_reference import (
    EnglishWikipediaPageReferenceSchema,
)
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReferenceSchema,
)


class TestEnglishWikipediaPageReferenceSchema(TestCase):
    def test_url_template1(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
        }

        reference = EnglishWikipediaPageReferenceSchema().load(data)
        console.print(reference)

    def test_url_template2(self):
        data = {"1": "chkchkchk.net", "template_name": "url"}
        reference = EnglishWikipediaPageReferenceSchema().load(data)
        console.print(reference)

    def test_parse_persons(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
        }

        reference = EnglishWikipediaPageReferenceSchema().load(data)
        reference.parse_persons()
        console.print(reference)
