from pydantic import BaseModel

from src.models.api.get_article_statistics.references.content.aggregate.cite_q_references import (
    CiteQReferences,
)
from src.models.api.get_article_statistics.references.content.aggregate.cs1_references import (
    Cs1References,
)


class AggregateContentReferences(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_article_statistics endpoint

    We use BaseModel to avoid the cache attribute"""

    # Bare URL references are used to mark up URLs which wikipedians
    # should improve with metadata to help others to find it in case
    # the link dies (idealy using the cite web template), see https://en.wikipedia.org/wiki/Wikipedia:Bare_URLs
    bare_url_t: int

    cs1_t: Cs1References

    # Has unique hash
    has_hash: int

    # Bare URL references are used to mark up URLs which wikipedians
    # should improve with metadata to help others to find it in case
    # the link dies (idealy using the cite web template), see https://en.wikipedia.org/wiki/Wikipedia:Bare_URLs
    # number_of_bare_url_references: int

    # Citation template, very similar to CS1 templates, see https://en.wikipedia.org/wiki/Template:Citation
    citation_t: int  # transcluded on 388k pages

    # Type of template using Wikidata, see https://en.wikipedia.org/wiki/Template:Cite_Q
    citeq_t: CiteQReferences  # transcluded on 42k pages

    # Reference with any content and 1+ template
    has_template: int

    # Content reference with any of the templates we support
    # any_supported_template: int

    # Type of template with no metadata https://en.wikipedia.org/wiki/Template:ISBN
    isbn_t: int  # transcluded on 459k pages

    # Reference that we could create a unique hash for using a reasonably stable identifier like DOI, QID, ISBN
    # number_of_hashed_content_references: int

    # Type of references with 2 or more templates found.
    multiple_t: int

    # Content reference with a CS1 template, Citation template or CiteQ template.
    # We prefer templates that are standardized and easy to generate a graph from
    supported_template_we_prefer: int

    # Type of template with no metadata https://en.wikipedia.org/wiki/Template:URL
    url_t: int  # transcluded on 363k pages

    # Type of reference with no template,
    # these cannot easily be converted to structured information without human intervention
    without_a_template: int

    # With at least one deprecated reference template
    with_deprecated_template: int
