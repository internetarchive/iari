from typing import List

from pydantic import BaseModel, Extra

from src.models.api.reference_statistics import ReferenceStatistics


class ArticleStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    # Bare URL references are used to mark up URLs which wikipedians
    # should improve with metadata to help others to find it in case
    # the link dies (idealy using the cite web template), see https://en.wikipedia.org/wiki/Wikipedia:Bare_URLs
    number_of_bare_url_references: int = 0

    # Reference inside a <ref> tag.
    number_of_citation_references: int = 0

    # Citation template, very similar to CS1 templates, see https://en.wikipedia.org/wiki/Template:Citation
    number_of_citation_template_references: int = 0  # transcluded on 388k pages

    # Type of template using Wikidata, see https://en.wikipedia.org/wiki/Template:Cite_Q
    number_of_citeq_references: int = 0  # transcluded on 42k pages

    # Reference with any content and 1+ template
    number_of_content_reference_with_at_least_one_template: int = 0

    # Type of reference with no template,
    # these cannot easily be converted to structured information without human intervention
    number_of_content_reference_with_no_templates: int = 0

    # Reference in- or outside a <ref> tag and with any content.
    number_of_content_references: int = 0

    # Content reference with a CS1 template, Citation template or CiteQ template.
    # We prefer templates that are standardized and easy to generate a graph from
    number_of_content_references_with_a_supported_template_we_prefer: int = 0

    # Content reference with any of the templates we support
    number_of_content_references_with_any_supported_template: int = 0

    # Number of references where we detected a CS1 template, see https://en.wikipedia.org/wiki/Help:Citation_Style_1
    # Transclusion statistics:
    # cite web 4420k pages
    # cite journal 912k pages
    # cite book 1520k pages
    number_of_cs1_references: int = 0

    # Reference outside a <ref> tag.
    number_of_general_references: int = 0

    # Reference that we could create a unique hash for using a reasonably stable identifier like DOI, QID, ISBN
    number_of_hashed_content_references: int = 0

    # Type of template with no metadata https://en.wikipedia.org/wiki/Template:ISBN
    number_of_isbn_template_references: int = 0  # transcluded on 459k pages

    # Type of references with 2 or more templates found.
    number_of_multiple_template_references: int = 0

    # Type of reference which does not have any content and only refer to another <ref> using a name
    number_of_named_references: int = 0

    # Type of template with no metadata https://en.wikipedia.org/wiki/Template:URL
    number_of_url_template_references: int = 0  # transcluded on 363k pages

    percent_of_content_references_with_a_hash: int = 0
    references: List[ReferenceStatistics] = []
    # TODO number_of_images
    # TODO number_of_words

    class Config:
        extra = Extra.forbid
