from typing import List

from pydantic import BaseModel

from src.models.api.reference_statistics import ReferenceStatistics


class ArticleStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    number_of_bare_url_references: int = 0
    number_of_citation_references: int = 0
    number_of_citation_template_references: int = 0
    number_of_citeq_references: int = 0
    number_of_content_reference_with_at_least_one_template: int = 0
    number_of_content_reference_with_no_templates: int = 0
    number_of_content_references: int = 0
    number_of_cs1_references: int = 0
    number_of_general_references: int = 0
    number_of_hashed_content_references: int = 0
    number_of_isbn_template_references: int = 0
    number_of_multiple_template_references: int = 0
    number_of_named_references: int = 0
    number_of_references_with_a_supported_template: int = 0
    number_of_url_template_references: int = 0
    percent_of_content_references_with_a_hash: int = 0
    references: List[ReferenceStatistics] = []
    # TODO number_of_images
    # TODO number_of_words
