from marshmallow import post_load

from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
    WikipediaPageReferenceSchema,
)


class EnglishWikipediaPageReference(WikipediaPageReference):
    pass


class EnglishWikipediaPageReferenceSchema(WikipediaPageReferenceSchema):
    @post_load
    def return_object(self, data, **kwargs):
        return EnglishWikipediaPageReference(**data)
