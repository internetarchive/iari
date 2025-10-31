from src import MissingInformationError
from src.models.v2.job import JobV2

from typing import Optional
from pydantic import BaseModel

class ExtractRefsJobV2(JobV2):
    """job that supports ExtractRefsV2 endpoint"""

    page_title: str = ""
    domain: str = "en.wikipedia.org"
    as_of: Optional[str] = None
    wikitext: str = ""

    wiki_id: str = ""
    wiki_page_title: str = ""
    wiki_revision: str = ""


    def validate_fields(self):
        """
        parameter checking here...

        must have at least "page_title" or "wikitext" defined
        """

        if not self.wikitext:
            if not self.page_title:
                raise MissingInformationError(
                    f"page_title or wikitext must be specified"
                )



