"""
Copyright Dennis Priskorn where not stated otherwise
"""
import logging
from typing import TYPE_CHECKING, List

import mwparserfromhell  # type: ignore
from mwparserfromhell.nodes import Tag  # type: ignore

import config
from src.models.exceptions import MissingInformationError, MultipleTemplateError
from src.models.wikibase import Wikibase
from src.models.wikimedia.wikipedia.reference.template import WikipediaTemplate
from src.wcd_base_model import WcdBaseModel

if TYPE_CHECKING:
    from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference

logger = logging.getLogger(__name__)


# TODO this does not scale at all if we want multi-wiki support :/
# TODO convert to abstract class and make an 2 implementations WikipediaRawCitationReference and WikipediaRawGeneralReference
class WikipediaRawReference(WcdBaseModel):
    """This class handles determining the type of reference and parse the templates from the raw reference

    This contains code from pywikibot 7.2.0 textlib.py to avoid forking the whole thing
    """

    # TODO make tag optional
    tag: Tag  # raw reference Tag from mwparserfromhell
    templates: List[WikipediaTemplate] = []
    plain_text_in_reference: bool = False
    citation_template_found: bool = True
    cs1_template_found: bool = False
    citeq_template_found: bool = False
    isbn_template_found: bool = False
    url_template_found: bool = False
    bare_url_template_found: bool = False
    testing: bool = False
    wikibase: Wikibase
    # TODO add new optional attribute wikicode: Optional[Wikicode]
    #  which contains the parsed output of the general reference line
    # TODO add new method is_from_ref that returns True if tag is not None

    class Config:
        arbitrary_types_allowed = True

    @property
    def number_of_templates(self) -> int:
        return len(self.templates)

    def __extract_templates_and_parameters_from_raw_reference__(self):
        """Helper method"""
        self.__extract_raw_templates__()
        self.__extract_and_clean_template_parameters__()

    def __extract_raw_templates__(self):
        """Extract the templates from the Tag"""
        # TODO rewrite to handle self.wikicode also
        if not self.tag:
            raise MissingInformationError("self.tag was None")
        if isinstance(self.tag, str):
            raise MissingInformationError("self.tag was str")
        # .contents is needed here to get a Wikicode object
        raw_templates = self.tag.contents.ifilter_templates(
            matches=lambda x: not x.name.lstrip().startswith("#"), recursive=True
        )
        for raw_template in raw_templates:
            self.templates.append(WikipediaTemplate(raw_template=raw_template))

    def __extract_and_clean_template_parameters__(self):
        """We only extract and clean if exactly one template is found"""
        if self.number_of_templates == 1:
            [template.extract_and_prepare_parameters() for template in self.templates]

    def __extract_and_determine_reference_type__(self):
        """Helper method"""
        self.__extract_templates_and_parameters_from_raw_reference__()
        self.__determine_reference_type__()

    def extract_determine_type_and_get_finished_wikipedia_reference_object(
        self,
    ) -> "WikipediaReference":
        """Get the WikipediaReference object"""
        self.__extract_and_determine_reference_type__()
        return self.make_wikipedia_reference_object()

    def make_wikipedia_reference_object(self) -> "WikipediaReference":
        """Make a WikipediaReference based on the extracted information"""
        from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference

        reference = WikipediaReference(**self.templates[0].parameters)
        # propagate attributes
        reference.raw_reference = self
        reference.cache = self.cache
        reference.wikibase = self.wikibase
        reference.finish_parsing_and_generate_hash(testing=self.testing)
        return reference

    def __determine_reference_type__(self):
        """We want to determine which type of reference this is

        Design limit: we only support one template for now"""
        if self.number_of_templates:
            if self.number_of_templates == 1:
                if self.__detect_clean_template__():
                    # We have a clean template reference like {{citeq|Q1}}
                    self.plain_text_in_reference = False
                else:
                    self.plain_text_in_reference = True
                if self.__detect_citation_template__():
                    self.citation_template_found = True
                else:
                    self.citation_template_found = False
                if self.__detect_cs1_template__():
                    self.cs1_template_found = True
                else:
                    self.cs1_template_found = False
                if self.__detect_citeq_template__():
                    self.citeq_template_found = True
                else:
                    self.citeq_template_found = False
                if self.__detect_isbn_template__():
                    self.isbn_template_found = True
                else:
                    self.isbn_template_found = False
                if self.__detect_url_template__():
                    self.url_template_found = True
                else:
                    self.url_template_found = False
                if self.__detect_bare_url_template__():
                    self.bare_url_template_found = True
                else:
                    self.bare_url_template_found = False
            else:
                # TODO log to file and fail gracely instead
                raise MultipleTemplateError(
                    f"We found multiple templates in "
                    f"{self.tag} which is currently not supported"
                )

    def __detect_clean_template__(self) -> bool:
        """A clean template reference has no text outside the {{ and }}"""
        if not self.templates[0].raw_template:
            raise MissingInformationError("self.templates[0].raw_template was None")
        if str(self.templates[0].raw_template).startswith("{{") and self.templates[
            0
        ].raw_template.endswith("}}"):
            return True
        else:
            return False

    def __detect_citation_template__(self) -> bool:
        if self.templates[0].name in config.citation_template:
            return True
        else:
            return False

    def __detect_cs1_template__(self) -> bool:
        if self.templates[0].name in config.cs1_templates:
            return True
        else:
            return False

    def __detect_citeq_template__(self):
        if self.templates[0].name in config.citeq_templates:
            return True
        else:
            return False

    def __detect_isbn_template__(self):
        if self.templates[0].name in config.isbn_template:
            return True
        else:
            return False

    def __detect_url_template__(self):
        if self.templates[0].name in config.url_template:
            return True
        else:
            return False

    def __detect_bare_url_template__(self):
        if config.bare_url_regex in self.templates[0].name:
            return True
        else:
            return False
