from marshmallow import post_load

from src.models.wikimedia.wikipedia.reference.english import EnglishWikipediaReference
from src.models.wikimedia.wikipedia.reference.schema import WikipediaReferenceSchema


class EnglishWikipediaReferenceSchema(WikipediaReferenceSchema):
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs):  # type: ignore
        return EnglishWikipediaReference(**data)
