from marshmallow import Schema, fields, post_load

from src.models.api.job import Job


class AddJobSchema(Schema):
    lang = fields.Str(required=True)
    site = fields.Str(required=True)
    testing = fields.Bool(required=False)
    title = fields.Str(required=True)

    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs):  # type: ignore
        return Job(**data)
