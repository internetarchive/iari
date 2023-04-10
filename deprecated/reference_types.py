# from pydantic import BaseModel
#
# from src.models.api.statistics.article.content import ContentReferences
#
#
# class ReferenceTypes(BaseModel):
#     """The purpose of this class is to model the statistics
#     the patron wants from the article endpoint
#
#     We use BaseModel to avoid the cache attribute"""
#
#     # Reference with content
#     content: ContentReferences
#     # Type of reference which does not have any content and only refer to another <ref> using a name
#     named: int
#
#     class Config:  # dead: disable
#         extra = "forbid"  # dead: disable
