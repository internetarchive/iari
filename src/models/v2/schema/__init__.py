from marshmallow import Schema, fields


class BaseSchemaV2(Schema):
    """
    provides always-there default parameters for API endpoint calls

    refresh:    re-fetch the data and re-fill the cached value, except of new fetch is error
    testing:    change behavior based on testing (* may not need this *)
    tag:        a pass thru value that helps with identifying object being queried
    """

    refresh = fields.Bool(required=False)
    showall = fields.Bool(required=False)
    testing = fields.Bool(required=False)
    hydrate = fields.Bool(required=False)
    uselocal = fields.Bool(required=False)
    tag = fields.Str(required=False)

    # def __init__(self, *args, request_method=None, **kwargs):
    #     # Extract or initialize context dict
    #     context = kwargs.pop("context", {}) or {}
    #
    #     # Add request_method if provided
    #     if request_method:
    #         context["request_method"] = request_method
    #
    #     # Pass merged context to Schema
    #     super().__init__(*args, context=context, **kwargs)