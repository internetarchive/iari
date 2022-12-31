from src.wcd_base_model import WcdBaseModel


class ArticleStatistics(WcdBaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_statistics endpoint"""
    number_of_cs1_references: int = 0
    number_of_citation_references: int = 0
    number_of_bare_url_references: int = 0
    number_of_citeq_references: int = 0
    number_of_isbn_template_references: int = 0
    number_of_multiple_template_references: int = 0
    number_of_named_references: int = 0
    number_of_content_references: int = 0
    number_of_hashed_content_references: int = 0
    percent_of_content_references_with_a_hash: int = 0
    # TODO number_of_images
    # TODO number_of_words
