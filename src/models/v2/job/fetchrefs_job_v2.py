import re
from urllib.parse import quote, unquote
from src.models.wikimedia.enums import WikimediaDomain
from src import MissingInformationError
from src.models.v2.job import JobV2
from typing import List


class FetchRefsJobV2(JobV2):
    """job that supports FetchRefsV2 endpoint"""

    # using marshmallow to describe parameters

    which_wiki: str = ""
    pages: List[str] = []
    wikitext: str = ""

    wiki_domain: WikimediaDomain = WikimediaDomain.wikipedia
    wiki_lang: str = ""

    wiki_id: str = ""
    wiki_page_title: str = ""
    wiki_revision: str = ""

    # @property
    # def quoted_title(self):
    #     if not self.wiki_page_title:
    #         raise MissingInformationError("self.wiki_page_title is empty")
    #     return quote(self.wiki_page_title, safe="")


    def validate_fields(self):
        """
        parameter checking done here...

        must have at "pages" or "wikitext" defined
        """

        from src import app

        # app.logger.error('fetchrefs validate_fields: Fake Error')
        # raise MissingInformationError(
        #     f'fetchrefs validate_fields: Fake Error'
        # )

        if not self.wikitext:
            if not self.pages:
                raise MissingInformationError(
                    f"pages or wikitext parameter must be specified"
                )



