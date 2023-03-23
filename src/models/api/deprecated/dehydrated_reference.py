# from typing import Any, Dict, List
#
# from pydantic import BaseModel
#
#
# class DehydratedReference(BaseModel):
#     """The purpose of this class is to model the statistics
#     the patron wants from the article endpoint
#
#     The dehydrated reference contain fewer details"""
#
#     id: str
#     type: List[str]  # [named|content]
#     subtype: List[str]  # [general|citation]
#     has_archive_details_url: bool
#     has_google_books_url_or_template: bool
#     has_web_archive_org_url: bool
#     identifiers: Dict[str, Any]  # {dois: [1234,12345], isbn: [1234]}
#     urls: List[str]
#     flds: List[str]  # first level domain strings
#     templates: int  # number of templates only
#
#     class Config:  # dead: disable
#         extra = "forbid"  # dead: disable
