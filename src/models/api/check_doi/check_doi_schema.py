from marshmallow import Schema
from marshmallow.fields import String


class CheckDoiSchema(Schema):
    """This validates the patron input in the get request"""

    doi = String()
