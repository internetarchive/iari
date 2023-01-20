from typing import Optional

from pydantic import BaseModel, Extra

from src.models.api.get_article_statistics.references import References


class ArticleStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    has_references: bool = False
    references: Optional[References] = None

    # TODO number_of_images
    # TODO number_of_words

    class Config:
        extra = Extra.forbid
