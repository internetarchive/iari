from marshmallow import Schema, fields


class BaseSchema(Schema):
    refresh = fields.Bool(required=False)
    testing = fields.Bool(required=False)
