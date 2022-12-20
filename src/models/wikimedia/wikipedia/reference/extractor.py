import logging
from typing import List
from typing import OrderedDict as OrderedDictType
from typing import Tuple

import mwparserfromhell  # type: ignore

import config
from src.models.wikibase import Wikibase
from src.wcd_base_model import WcdBaseModel
from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference
from src.models.wikimedia.wikipedia.reference.raw_reference import WikipediaRawReference

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
    __raw_references: List[WikipediaRawReference] = [] # private
    references: List[WikipediaReference] = []
    number_of_references_with_one_supported_template: int = 0
    wikibase: Wikibase
    testing: bool = False

    @property
    def number_of_references(self) -> int:
        return len(self.references)

    @property
    def number_of_hashed_references(self):
        return len(
            [
                reference
                for reference in self.references
                if reference.md5hash is not None
            ]
        )

    @property
    def percent_of_references_with_a_hash(self):
        if self.number_of_references == 0:
            return 0
        else:
            return int(
                self.number_of_hashed_references * 100 / self.number_of_references
            )

    def __extract_all_raw_references__(self):
        """This extracts everything inside <ref></ref> tags"""
        # Thanks to https://github.com/JJMC89,
        # see https://github.com/earwig/mwparserfromhell/discussions/295#discussioncomment-4392452
        wikicode = mwparserfromhell.parse(self.wikitext)
        refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
        for ref in refs:
            self.__raw_references.append(WikipediaRawReference(tag=ref, wikibase=self.wikibase, testing=self.testing))

    def extract_all_references(self):
        self.__extract_all_raw_references__()
        self.references = [raw_reference.extract_determine_type_and_get_finished_wikipedia_reference_object() for raw_reference in self.__raw_references]

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
