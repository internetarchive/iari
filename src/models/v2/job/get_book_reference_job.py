# import re
# from urllib.parse import quote, unquote
# #
# # import requests
# #
# # import config
# # from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
# from src.models.wikimedia.enums import WikimediaDomain
# from src import MissingInformationError
from src.models.v2.job import JobV2


class GetBookReferenceJobV2(JobV2):
    """job that supports GetBookReferenceV2 endpoint"""

    book_ref: str = ""


    def validate_fields(self):
        """
        any parameter checking done here...

        must have at least "book_ref" defined, handled in schema
        """

