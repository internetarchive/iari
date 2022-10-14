from marshmallow import post_load

from src.models.wikimedia.wikipedia.reference.schema import WikipediaReferenceSchema


class EnglishWikipediaReferenceSchema(WikipediaReferenceSchema):
    @post_load
    # **kwargs is needed here despite what the validator claims
    def return_object(self, data, **kwargs):  # type: ignore
        from src.models.wikimedia.wikipedia.reference.english.english_reference import (
            EnglishWikipediaReference,
        )

        return EnglishWikipediaReference(**data)
