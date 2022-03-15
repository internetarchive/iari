from pprint import pprint
from unittest import TestCase

from marshmallow import Schema, fields, ValidationError

from src import console
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReferenceSchema,
)


class TestWikipediaPageReferenceSchema(TestCase):
    def test_marshmellow(self):
        class UserSchema(Schema):
            name = fields.String(required=True)
            age = fields.Integer(required=True)

        result = UserSchema().load({"age": 42}, partial=("name",))

        class BandMemberSchema(Schema):
            name = fields.String(required=True)
            email = fields.Email()

        user_data = [
            {"email": "mick@stones.com", "name": "Mick"},
            {"email": "invalid", "name": "Invalid"},  # invalid email
            {"email": "keith@stones.com", "name": "Keith"},
            {"email": "charlie@stones.com"},  # missing "name"
        ]

        try:
            BandMemberSchema(many=True).load(user_data)
        except ValidationError as err:
            pprint(err.messages)

    def test_template(self):
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

        reference = English().load(data)
        console.print(reference)

    def test_url_template(self):
        data = {"1": "chkchkchk.net", "template_name": "url"}
        schema = WikipediaPageReferenceSchema()
        reference = schema.load(data)
        console.print(reference)
