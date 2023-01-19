from typing import Dict, Optional

from pydantic import BaseModel, Extra

from src.models.api.get_statistics.references import References


class ArticleStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    first_level_domain_counts: Dict[str, int] = {}
    has_references: bool = False
    references: Optional[References] = None

    # TODO number_of_images
    # TODO number_of_words

    class Config:
        extra = Extra.forbid
