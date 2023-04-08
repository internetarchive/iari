# from marshmallow import post_load
#
# from src.models.wikimedia.wikipedia.reference.schema import WikipediaReferenceSchema
#
#
# class EnglishWikipediaReferenceSchema(WikipediaReferenceSchema):
#     # noinspection PyUnusedLocal
#     @post_load
#     # **kwargs is needed here despite what the validator claims
#     def return_object(self, data, **kwargs):  # type: ignore # dead: disable
#         from src.models.wikimedia.wikipedia.reference.english.english_reference import (
#             EnglishWikipediaReference,
#         )
#
#         return EnglishWikipediaReference(**data)
