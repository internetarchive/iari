from marshmallow import Schema, fields


class BaseSchemaV2(Schema):
    """
    provides always-there default parameters for API endpoint calls

    refresh:    re-fetch the data and re-fill the cached value, except of new fetch is error
    testing:    change behavior based on testing (* may not need this *)
    tag:        a pass thru value that helps with identifying object being queried
    """

    refresh = fields.Bool(required=False)
    testing = fields.Bool(required=False)
    tag = fields.Str(required=False)
