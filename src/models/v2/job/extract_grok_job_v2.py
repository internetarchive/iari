from src import MissingInformationError
from src.models.v2.job import JobV2

from typing import Optional
from pydantic import BaseModel

class ExtractGrokJobV2(JobV2):
    """job that supports ExtractRefsV2 endpoint"""

    page_title: str = ""
    use_local_cache: bool = False

    def validate_fields(self):
        """
        parameter checking here...
        """
        pass


