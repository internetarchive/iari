from marshmallow import Schema, fields


class BaseSchemaV2(Schema):
    """
    provides always-there default parameters for API endpoint calls
    """

    refresh = fields.Bool(required=False)
    testing = fields.Bool(required=False)
