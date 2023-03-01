from marshmallow import Schema
from marshmallow.fields import Int, String


class ReferencesSchema(Schema):
    offset = Int()
    wari_id = String()
