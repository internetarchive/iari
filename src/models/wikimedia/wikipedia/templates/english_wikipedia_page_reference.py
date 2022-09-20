from marshmallow import post_load

from src.models.wikimedia.wikipedia.templates.wikipedia_reference import (
    WikipediaPageReferenceSchema,
    WikipediaReference,
)


class EnglishWikipediaReference(WikipediaReference):
    pass


class EnglishWikipediaPageReferenceSchema(WikipediaPageReferenceSchema):
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs):  # type: ignore
        return EnglishWikipediaReference(**data)
