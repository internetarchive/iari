from marshmallow import Schema
from marshmallow.fields import Int, String


class CheckUrlSchema(Schema):
    """This validates the patron input in the get request"""

    url = String()
    timeout = Int()
