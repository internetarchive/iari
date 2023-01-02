import logging
from typing import List
from typing import OrderedDict as OrderedDictType
from typing import Tuple

import mwparserfromhell  # type: ignore

import config
from src.models.wikibase import Wikibase
from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference
from src.models.wikimedia.wikipedia.reference.raw_reference import WikipediaRawReference
from src.wcd_base_model import WcdBaseModel

Triple_list = List[Tuple[str, OrderedDictType[str, str], str]]

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class WikipediaReferenceExtractor(WcdBaseModel):
    """This class handles all extraction of references from wikicode

    Design:
    * first we get the wikicode
    * we parse it with mwparser from hell
    * we extract the raw references -> WikipediaRawReference
    """

    wikitext: str
    raw_references: List[WikipediaRawReference] = []  # private
    references: List[WikipediaReference] = []
    # number_of_references_with_one_supported_template: int = 0
    wikibase: Wikibase
    testing: bool = False

    # TODO rewrite to distinguish between citation aka refreferences and general references outside a </ref>.
    # TODO add number_of_citation_references method
    # TODO add number_of_general_references method
    # TODO add number_of_references_with_a_template using list comprehension and if wrr.templates
    # TODO add number_of_references_with_a_supported_citation_template using list comprehension and if wrr.has_supported_citation_template

    @property
    def content_references_without_templates(self):
        return [
            reference
            for reference in self.content_references
            if reference.raw_reference.number_of_templates == 0
        ]

    @property
    def number_of_content_reference_with_no_templates(self):
        return len(self.content_references_without_templates)

    @property
    def content_references_with_at_least_one_template(self):
        return [
            reference
            for reference in self.content_references
            if reference.raw_reference.number_of_templates >= 1
        ]

    @property
    def number_of_content_reference_with_at_least_one_template(self):
        return len(self.content_references_with_at_least_one_template)

    @property
    def cs1_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.cs1_template_found
        ]

    @property
    def number_of_cs1_references(self):
        return len(self.cs1_references)

    @property
    def citation_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.citation_template_found
        ]

    @property
    def number_of_citation_references(self):
        return len(self.citation_references)

    @property
    def bare_url_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.bare_url_template_found
        ]

    @property
    def number_of_bare_url_references(self):
        return len(self.bare_url_references)

    @property
    def citeq_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.citeq_template_found
        ]

    @property
    def number_of_citeq_references(self):
        return len(self.citeq_references)

    @property
    def isbn_template_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.isbn_template_found
        ]

    @property
    def number_of_isbn_template_references(self):
        return len(self.isbn_template_references)

    @property
    def multiple_template_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.multiple_templates_found
        ]

    @property
    def number_of_multiple_template_references(self):
        return len(self.multiple_template_references)

    @property
    def named_references(self):
        """Special type of reference with no content
        Example: <ref name="INE"/>"""
        return [
            reference
            for reference in self.references
            if reference.raw_reference.is_named_reference
        ]

    @property
    def number_of_named_references(self):
        return len(self.named_references)

    @property
    def content_references(self):
        """This is references with actual content beyond a name"""
        return [
            reference
            for reference in self.references
            if not reference.raw_reference.is_named_reference
        ]

    @property
    def number_of_content_references(self):
        return len(self.content_references)

    @property
    def number_of_raw_references(self) -> int:
        return len(self.raw_references)

    @property
    def number_of_references(self) -> int:
        return len(self.references)

    @property
    def number_of_hashed_content_references(self):
        return len(
            [
                reference
                for reference in self.content_references
                if reference.md5hash is not None
            ]
        )

    @property
    def percent_of_content_references_with_a_hash(self):
        if self.number_of_content_references == 0:
            return 0
        else:
            return int(
                self.number_of_hashed_content_references
                * 100
                / self.number_of_content_references
            )

    # TODO rename to citation_references
    def __extract_all_raw_references__(self):
        """This extracts everything inside <ref></ref> tags"""
        logger.debug("__extract_all_raw_references__: running")
        # Thanks to https://github.com/JJMC89,
        # see https://github.com/earwig/mwparserfromhell/discussions/295#discussioncomment-4392452
        wikicode = mwparserfromhell.parse(self.wikitext)
        refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
        for ref in refs:
            self.raw_references.append(
                WikipediaRawReference(
                    tag=ref, wikibase=self.wikibase, testing=self.testing
                )
            )

    def extract_all_references(self):
        """Extract all references from self.wikitext"""
        logger.debug("extract_all_references: running")
        self.__extract_all_raw_references__()
        self.__parse_all_raw_references__()
        self.__convert_raw_references_to_reference_objects__()
        # We guard for None here

    # def prepare_all_statistic(self):
    #     # TODO figure out how to best store this data in the wikibase
    #     self.__count_number_of_supported_templates_found__()
    #
    # def __count_number_of_supported_templates_found__(self):
    #     if self.number_of_references:
    #         self.number_of_references_with_a_template =
    #         self.number_of_references_with_one_template =
    #         self.number_of_references_with_multiple_templates =
    #         self.number_of_references_with_a_supported_template =
    #         self.number_of_references_with_one_supported_template =
    #         self.number_of_references_with_plain_text_only =
    #         self.number_of_references_with_a_bare_url_template =
    #         self.number_of_references_with_a_isbn_template =
    #         self.number_of_references_with_a_url_template =
    #         self.number_of_references_with_a_bare_url_template =
    #         self.number_of_references_with_a_bare_url_pdf_template =
    def __convert_raw_references_to_reference_objects__(self):
        self.references = [
            raw_reference.get_finished_wikipedia_reference_object()
            for raw_reference in self.raw_references
        ]

    def __parse_all_raw_references__(self):
        for wrr in self.raw_references:
            wrr.extract_and_determine_reference_type()
