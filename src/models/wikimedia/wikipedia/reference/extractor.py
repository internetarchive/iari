import logging
import re
from typing import List
from typing import OrderedDict as OrderedDictType
from typing import Tuple

import mwparserfromhell  # type: ignore
from mwparserfromhell.wikicode import Wikicode  # type: ignore

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
    wikicode: Wikicode = None
    raw_references: List[WikipediaRawReference] = []  # private
    references: List[WikipediaReference] = []
    sections: List[Wikicode] = []
    wikibase: Wikibase
    testing: bool = False

    class Config:
        arbitrary_types_allowed = True

    @property
    def percent_of_content_references_without_a_template(self) -> int:
        if self.number_of_content_references == 0:
            return 0
        return int(
            (self.number_of_content_reference_without_a_template * 100)
            / self.number_of_content_references
        )

    @property
    def number_of_url_template_references(self) -> int:
        return len(self.url_template_references)

    @property
    def url_template_references(self):
        return [
            reference
            for reference in self.content_references
            if reference.raw_reference.url_template_found
        ]

    @property
    def number_of_sections_found(self) -> int:
        if not self.sections:
            self.__extract_sections__()
        return len(self.sections)

    @property
    def general_references(self):
        return [
            reference
            for reference in self.content_references
            if reference.raw_reference.is_general_reference
        ]

    @property
    def number_of_general_references(self) -> int:
        return len(self.general_references)

    @property
    def number_of_content_references_with_any_supported_template(self) -> int:
        return len(
            [
                reference
                for reference in self.content_references
                if (
                    reference.raw_reference.number_of_templates > 0
                    and (
                        reference.raw_reference.cs1_template_found
                        or reference.raw_reference.isbn_template_found
                        or reference.raw_reference.citeq_template_found
                        or reference.raw_reference.citation_template_found
                        or reference.raw_reference.bare_url_template_found
                    )
                )
            ]
        )

    @property
    def number_of_content_references_with_a_supported_template_we_prefer(self) -> int:
        """We prefer templates that is easy to generate a graph from
        Currently that is CS1 templates, CiteQ template and Citation template"""
        return len(
            [
                reference
                for reference in self.content_references
                if (
                    reference.raw_reference.number_of_templates > 0
                    and (
                        reference.raw_reference.cs1_template_found
                        or reference.raw_reference.citeq_template_found
                        or reference.raw_reference.citation_template_found
                    )
                )
            ]
        )

    @property
    def content_references_without_templates(self):
        return [
            reference
            for reference in self.content_references
            if reference.raw_reference.number_of_templates == 0
        ]

    @property
    def number_of_content_reference_without_a_template(self) -> int:
        return len(self.content_references_without_templates)

    @property
    def content_references_with_at_least_one_template(self):
        return [
            reference
            for reference in self.content_references
            if reference.raw_reference.number_of_templates >= 1
        ]

    @property
    def number_of_content_reference_with_at_least_one_template(self) -> int:
        return len(self.content_references_with_at_least_one_template)

    @property
    def cs1_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.cs1_template_found
        ]

    @property
    def number_of_cs1_references(self) -> int:
        return len(self.cs1_references)

    @property
    def citation_references(self):
        return [
            reference
            for reference in self.content_references
            if reference.raw_reference.is_citation_reference
        ]

    @property
    def number_of_citation_references(self) -> int:
        return len(self.citation_references)

    @property
    def citation_template_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.citation_template_found
        ]

    @property
    def number_of_citation_template_references(self) -> int:
        return len(self.citation_template_references)

    @property
    def bare_url_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.bare_url_template_found
        ]

    @property
    def number_of_bare_url_references(self) -> int:
        return len(self.bare_url_references)

    @property
    def citeq_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.citeq_template_found
        ]

    @property
    def number_of_citeq_references(self) -> int:
        return len(self.citeq_references)

    @property
    def isbn_template_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.isbn_template_found
        ]

    @property
    def number_of_isbn_template_references(self) -> int:
        return len(self.isbn_template_references)

    @property
    def multiple_template_references(self):
        return [
            reference
            for reference in self.references
            if reference.raw_reference.multiple_templates_found
        ]

    @property
    def number_of_multiple_template_references(self) -> int:
        return len(self.multiple_template_references)

    @property
    def empty_named_references(self):
        """Special type of reference with no content
        Example: <ref name="INE"/>"""
        return [
            reference
            for reference in self.references
            if reference.raw_reference.is_named_reference
        ]

    @property
    def number_of_empty_named_references(self) -> int:
        return len(self.empty_named_references)

    @property
    def content_references(self):
        """This is references with actual content beyond a name"""
        return [
            reference
            for reference in self.references
            if not reference.raw_reference.is_named_reference
        ]

    @property
    def number_of_content_references(self) -> int:
        return len(self.content_references)

    @property
    def number_of_raw_references(self) -> int:
        return len(self.raw_references)

    @property
    def number_of_references(self) -> int:
        return len(self.references)

    @property
    def number_of_hashed_content_references(self) -> int:
        return len(
            [reference for reference in self.content_references if reference.md5hash]
        )

    @property
    def percent_of_content_references_with_a_hash(self) -> int:
        if self.number_of_content_references == 0:
            return 0
        else:
            return int(
                self.number_of_hashed_content_references
                * 100
                / self.number_of_content_references
            )

    def __extract_all_raw_citation_references__(self):
        """This extracts everything inside <ref></ref> tags"""
        logger.debug("__extract_all_raw_citation_references__: running")
        # Thanks to https://github.com/JJMC89,
        # see https://github.com/earwig/mwparserfromhell/discussions/295#discussioncomment-4392452
        self.__parse_wikitext__()
        # tag = Tag
        # tag.tag
        refs = self.wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
        logger.debug(f"Number of refs found: {len(refs)}")
        for ref in refs:
            self.raw_references.append(
                WikipediaRawReference(
                    wikicode=ref, wikibase=self.wikibase, testing=self.testing
                )
            )

    def __extract_all_raw_general_references__(self):
        """This extracts everything inside <ref></ref> tags"""
        logger.debug("__extract_all_raw_general_references__: running")
        # Thanks to https://github.com/JJMC89,
        # see https://github.com/earwig/mwparserfromhell/discussions/295#discussioncomment-4392452
        self.__extract_sections__()
        for section in self.sections:
            # Get section line by line
            lines = str(section).split("\n")
            logger.debug(f"Extracting {len(lines)} lines form section {lines[0]}")
            for line in lines:
                logger.info(f"Working on line: {line}")
                # Guard against empty line
                if line:
                    logger.debug("Parsing line")
                    parsed_line = mwparserfromhell.parse(line)
                    heading_found = bool("==" in line)
                    logger.info(f"Heading found in line {bool(heading_found)}")
                    if not heading_found:
                        logger.debug("Appending to self.raw_references")
                        # We don't know what the line contains so we assume it is a reference
                        self.raw_references.append(
                            WikipediaRawReference(
                                wikicode=parsed_line,
                                wikibase=self.wikibase,
                                testing=self.testing,
                                is_general_reference=True,
                            )
                        )

    def extract_all_references(self):
        """Extract all references from self.wikitext"""
        logger.debug("extract_all_references: running")
        self.__parse_wikitext__()
        self.__extract_all_raw_citation_references__()
        self.__extract_all_raw_general_references__()
        self.__parse_templates_and_determine_type_on_raw_references__()
        self.__convert_raw_references_to_reference_objects__()

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
        logger.debug("__convert_raw_references_to_reference_objects__: running")
        self.references = [
            raw_reference.get_finished_wikipedia_reference_object()
            for raw_reference in self.raw_references
        ]

    def __parse_templates_and_determine_type_on_raw_references__(self):
        logger.debug("__parse_all_raw_references__: running")
        for wrr in self.raw_references:
            wrr.extract_and_determine_reference_type()

    def __extract_sections__(self):
        logger.debug("__extract_sections__: running")
        if not self.wikicode:
            self.__parse_wikitext__()
        self.sections: List[Wikicode] = self.wikicode.get_sections(
            levels=[2],
            matches="bibliography|further reading",
            flags=re.I,
            include_headings=False,
        )
        logger.debug(f"Number of sections found: {len(self.sections)}")

    def __parse_wikitext__(self):
        logger.debug("__parse_wikitext__: running")
        if not self.wikicode:
            self.wikicode = mwparserfromhell.parse(self.wikitext)
