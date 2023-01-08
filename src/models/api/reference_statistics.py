from pydantic import BaseModel


class ReferenceStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the user wants from the get_statistics endpoint"""

    plain_text_in_reference: bool = False
    citation_template_found: bool = False
    cs1_template_found: bool = False
    citeq_template_found: bool = False
    isbn_template_found: bool = False
    url_template_found: bool = False
    bare_url_template_found: bool = False
    multiple_templates_found: bool = False
    is_named_reference: bool = False
    wikitext: str = ""
    is_citation_reference: bool = False
    is_general_reference: bool = False
