from marshmallow import Schema, fields


class RefreshSchema(Schema):
    refresh = fields.Bool(required=False)
