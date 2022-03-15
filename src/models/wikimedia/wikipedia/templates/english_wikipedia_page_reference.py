from marshmallow import post_load

from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
    WikipediaPageReferenceSchema,
)


class EnglishWikipediaPageReference(WikipediaPageReference):
    pass


class EnglishWikipediaPageReferenceSchema(WikipediaPageReferenceSchema):
    @post_load
    def make_user(self, data, **kwargs):
        from src.models.wikimedia.wikipedia.templates.english_wikipedia_page_reference import (
            EnglishWikipediaPageReference,
        )

        return EnglishWikipediaPageReference(**data)
