import logging
import re
from typing import Dict, List

import mwparserfromhell  # type: ignore
from mwparserfromhell.wikicode import Wikicode  # type: ignore

import config
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference
from src.models.wikimedia.wikipedia.reference.raw_reference import WikipediaRawReference
from src.models.wikimedia.wikipedia.url import WikipediaUrl
from src.wcd_base_model import WcdBaseModel

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
    # wikibase: Wikibase
    testing: bool = False
    check_urls: bool = False
    check_urls_done: bool = False
    checked_and_unique_reference_urls: List[WikipediaUrl] = []
    language_code: str = ""

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    # @property
    # def number_of_content_references_with_url_found(self):
    #     return len(
    #         [
    #             reference
    #             for reference in self.content_references
    #             if reference.raw_reference.url_found
    #         ]
    #     )

    @property
    def has_references(self):
        """Helper method"""
        return bool(self.number_of_references)

    # @property
    # def number_of_references_with_a_deprecated_template(self) -> int:
    #     return len(
    #         [
    #             reference
    #             for reference in self.content_references
    #             if reference.raw_reference.deprecated_reference_template_found
    #         ]
    #     )
    #
    # @property
    # def number_of_other_cs1_references(self):
    #     """All other CS1 templates that we don't especially care about"""
    #     return len(
    #         [
    #             reference
    #             for reference in self.content_references
    #             if reference.raw_reference.cs1_template_found
    #             and not (
    #                 reference.raw_reference.cite_web_template_found
    #                 or reference.raw_reference.cite_book_template_found
    #                 or reference.raw_reference.cite_journal_template_found
    #             )
    #         ]
    #     )
    #
    # @property
    # def number_of_cite_journal_references_with_doi(self):
    #     return len([ref for ref in self.cite_journal_references if ref.doi])
    #
    # @property
    # def number_of_cite_web_references_with_google_books_link_or_template(self):
    #     return len(
    #         [
    #             ref
    #             for ref in self.cite_web_references
    #             if ref.raw_reference.google_books_url_or_template_found
    #         ]
    #     )
    #
    # @property
    # def number_of_cite_book_references_with_isbn(self):
    #     return len([ref for ref in self.cite_book_references if ref.isbn])
    #
    # @property
    # def number_of_cite_web_references_with_a_url(self):
    #     return self.number_of_content_references_with_a_url(
    #         list_=self.cite_web_references
    #     )
    #
    # @property
    # def number_of_cite_web_references_with_ia_details_link(self):
    #     return self.number_of_content_references_with_ia_details_link(
    #         list_=self.cite_web_references
    #     )
    #
    # @property
    # def number_of_cite_web_references_with_wm_link(self):
    #     return self.number_of_content_references_with_wm_link(
    #         list_=self.cite_web_references
    #     )
    #
    # @property
    # def number_of_cite_journal_references_with_a_url(self):
    #     return self.number_of_content_references_with_a_url(
    #         list_=self.cite_journal_references
    #     )
    #
    # @property
    # def number_of_cite_journal_references_with_ia_details_link(self):
    #     return self.number_of_content_references_with_ia_details_link(
    #         list_=self.cite_journal_references
    #     )
    #
    # @property
    # def number_of_cite_journal_references_with_wm_link(self):
    #     return self.number_of_content_references_with_wm_link(
    #         list_=self.cite_journal_references
    #     )
    #
    # @property
    # def number_of_cite_book_references_with_a_url(self):
    #     return self.number_of_content_references_with_a_url(
    #         list_=self.cite_book_references
    #     )
    #
    # @property
    # def number_of_cite_book_references_with_ia_details_link(self):
    #     return self.number_of_content_references_with_ia_details_link(
    #         list_=self.cite_book_references
    #     )
    #
    # @property
    # def number_of_cite_book_references_with_wm_link(self):
    #     return self.number_of_content_references_with_wm_link(
    #         list_=self.cite_book_references
    #     )
    #
    # @property
    # def number_of_cite_book_references(self):
    #     return len(self.cite_book_references)
    #
    # @property
    # def cite_web_references(self):
    #     return [
    #         reference
    #         for reference in self.references
    #         if reference.raw_reference.cite_web_template_found
    #     ]
    #
    # @property
    # def cite_book_references(self):
    #     return [
    #         reference
    #         for reference in self.references
    #         if reference.raw_reference.cite_book_template_found
    #     ]
    #
    # @property
    # def number_of_cite_journal_references(self):
    #     return len(self.cite_journal_references)
    #
    # @property
    # def cite_journal_references(self):
    #     return [
    #         reference
    #         for reference in self.references
    #         if reference.raw_reference.cite_journal_template_found
    #     ]
    #
    # @property
    # def number_of_cite_web_references(self):
    #     return len(
    #         [
    #             reference
    #             for reference in self.references
    #             if reference.raw_reference.cite_web_template_found
    #         ]
    #     )

    # @property
    # def reference_urls_dictionaries(self):
    #     """List of URLs as dictionaries ready for API digestion"""
    #     if not self.check_urls_done:
    #         raise MissingInformationError("self.check_urls_done was False")
    #     return [url.dict() for url in self.checked_and_unique_reference_urls]

    # @property
    # def number_of_unique_reference_urls_with_malformed_url(self):
    #     """This can be True while error is also True"""
    #     if not self.check_urls_done:
    #         raise MissingInformationError("self.check_urls_done was False")
    #     return len(self.malformed_urls)

    # @property
    # def malformed_urls(self) -> List[str]:
    #     """List of malformed_urls"""
    #     return [
    #         url.url
    #         for url in self.checked_and_unique_reference_urls
    #         if url.malformed_url is True
    #     ]

    # @property
    # def number_of_urls(self):
    #     """Non-unique URLs"""
    #     return len(self.urls)

    @property
    def urls(self) -> List[WikipediaUrl]:
        """List of non-unique urls"""
        urls: List[WikipediaUrl] = list()
        for reference in self.references:
            if reference.raw_reference:
                for url in reference.raw_reference.reference_urls:
                    urls.append(url)
        return urls

    @property
    def raw_urls(self) -> List[str]:
        """List of raw non-unique urls found in the reference"""
        urls: List[str] = list()
        for reference in self.references:
            if reference.raw_reference:
                for url in reference.raw_reference.reference_urls:
                    urls.append(url.url)
        return urls

    # @property
    # def number_of_checked_unique_reference_urls(self):
    #     """Unique URLs"""
    #     if not self.check_urls_done:
    #         raise MissingInformationError("self.check_urls_done was False")
    #     return len(self.checked_and_unique_reference_urls)

    # def __get_checked_and_unique_reference_urls_from_references__(self) -> None:
    #     """Get and check unique URLs
    #     If check_urls is not enabled we do nothing."""
    #     if self.check_urls:
    #         if not self.check_urls_done:
    #             raise MissingInformationError("url checking has not been done yet")
    #         if len(self.raw_references) != len(self.references):
    #             raise MissingInformationError(
    #                 "conversion to references has not been done yet"
    #             )
    #         urls: List[WikipediaUrl] = list()
    #         for reference in self.references:
    #             if reference.raw_reference:
    #                 for url in reference.raw_reference.checked_urls:
    #                     urls.append(url)
    #         # We run them through a set to avoid duplicates and then convert back
    #         # to list because objects in sets cannot be updated it seems
    #         self.checked_and_unique_reference_urls = list(set(urls))

    @property
    def reference_first_level_domain_counts(self) -> Dict[str, int]:
        """This returns a dict with fld as key and the count as value"""
        fld_set = set(self.reference_first_level_domains)
        counts = dict()
        for fld in fld_set:
            count = self.reference_first_level_domains.count(fld)
            counts[fld] = count
        # Sort by count, descending
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        # Thanks to Sawood for recommending we simplify and return a dictionary
        sorted_counts_dictionary = {}
        for element in sorted_counts:
            fld = str(element[0])
            count = int(element[1])
            sorted_counts_dictionary[fld] = count
        return sorted_counts_dictionary

    @property
    def reference_first_level_domains(self) -> List[str]:
        """This is a list and duplicates are likely and wanted"""
        if not self.content_references:
            return []
        flds = []
        for reference in self.content_references:
            if not reference.raw_reference.first_level_domains_done:
                reference.raw_reference.__extract_first_level_domains__()
            for fld in reference.raw_reference.first_level_domains:
                flds.append(fld)
        return flds

    # @property
    # def number_of_url_template_references(self) -> int:
    #     return len(self.url_template_references)

    # @property
    # def url_template_references(self):
    #     return [
    #         reference
    #         for reference in self.content_references
    #         if reference.raw_reference.url_template_found
    #     ]

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

    # @property
    # def number_of_content_references_with_any_supported_template(self) -> int:
    #     return len(
    #         [
    #             reference
    #             for reference in self.content_references
    #             if (
    #                 reference.raw_reference.number_of_templates > 0
    #                 and (
    #                     reference.raw_reference.cs1_template_found
    #                     or reference.raw_reference.isbn_template_found
    #                     or reference.raw_reference.citeq_template_found
    #                     or reference.raw_reference.citation_template_found
    #                     or reference.raw_reference.bare_url_template_found
    #                 )
    #             )
    #         ]
    #     )

    # @property
    # def number_of_content_references_with_a_supported_template_we_prefer(self) -> int:
    #     """We prefer templates that is easy to generate a graph from
    #     Currently that is CS1 templates, CiteQ templates and Citation templates"""
    #     return len(
    #         [
    #             reference
    #             for reference in self.content_references
    #             if (
    #                 reference.raw_reference.number_of_templates > 0
    #                 and (
    #                     reference.raw_reference.cs1_template_found
    #                     or reference.raw_reference.citeq_template_found
    #                     or reference.raw_reference.citation_template_found
    #                 )
    #             )
    #         ]
    #     )

    # @property
    # def content_references_without_templates(self):
    #     return [
    #         reference
    #         for reference in self.content_references
    #         if reference.raw_reference.number_of_templates == 0
    #     ]

    # @property
    # def number_of_content_reference_without_a_template(self) -> int:
    #     return len(self.content_references_without_templates)
    #
    # @property
    # def content_references_with_at_least_one_template(self):
    #     return [
    #         reference
    #         for reference in self.content_references
    #         if reference.raw_reference.number_of_templates >= 1
    #     ]
    #
    # @property
    # def number_of_content_reference_with_at_least_one_template(self) -> int:
    #     return len(self.content_references_with_at_least_one_template)
    #
    # @property
    # def cs1_references(self):
    #     return [
    #         reference
    #         for reference in self.references
    #         if reference.raw_reference.cs1_template_found
    #     ]

    # @property
    # def number_of_cs1_references(self) -> int:
    #     return len(self.cs1_references)

    @property
    def citation_references(self):
        return [
            reference
            for reference in self.content_references
            if reference.raw_reference.is_footnote_reference
        ]

    @property
    def number_of_citation_references(self) -> int:
        return len(self.citation_references)

    # @property
    # def citation_template_references(self):
    #     return [
    #         reference
    #         for reference in self.references
    #         if reference.raw_reference.citation_template_found
    #     ]

    # @property
    # def number_of_citation_template_references(self) -> int:
    #     return len(self.citation_template_references)

    # @property
    # def bare_url_references(self):
    #     return [
    #         reference
    #         for reference in self.references
    #         if reference.raw_reference.bare_url_template_found
    #     ]

    # @property
    # def number_of_bare_url_references(self) -> int:
    #     return len(self.bare_url_references)

    # @property
    # def citeq_references(self):
    #     return [
    #         reference
    #         for reference in self.references
    #         if reference.raw_reference.citeq_template_found
    #     ]
    #
    # @property
    # def number_of_citeq_references(self) -> int:
    #     return len(self.citeq_references)

    # @property
    # def isbn_template_references(self):
    #     return [
    #         reference
    #         for reference in self.references
    #         if reference.raw_reference.isbn_template_found
    #     ]
    #
    # @property
    # def number_of_isbn_template_references(self) -> int:
    #     return len(self.isbn_template_references)
    #
    # @property
    # def multiple_template_references(self):
    #     return [
    #         reference
    #         for reference in self.references
    #         if reference.raw_reference.multiple_templates_found
    #     ]
    #
    # @property
    # def number_of_multiple_template_references(self) -> int:
    #     return len(self.multiple_template_references)

    @property
    def empty_named_references(self):
        """Special type of reference with no content
        Example: <ref name="INE"/>"""
        return [
            reference
            for reference in self.references
            if reference.raw_reference.is_empty_named_reference
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
            if not reference.raw_reference.is_empty_named_reference
        ]

    @property
    def number_of_content_references(self) -> int:
        return len(self.content_references)

    # @property
    # def number_of_raw_references(self) -> int:
    #     return len(self.raw_references)

    @property
    def number_of_references(self) -> int:
        return len(self.references)

    # @property
    # def number_of_hashed_content_references(self) -> int:
    #     return len(
    #         [reference for reference in self.content_references if reference.md5hash]
    #     )

    # def number_of_content_references_with_google_books_template_or_url(
    #     self, list_: List[WikipediaReference] = None
    # ) -> int:
    #     if list_ is None:
    #         list_ = self.content_references
    #     result = len(
    #         [
    #             ref
    #             for ref in list_
    #             if ref.raw_reference
    #             and ref.raw_reference.google_books_url_or_template_found
    #         ]
    #     )
    #     return result

    def number_of_content_references_with_a_url(
        self, list_: List[WikipediaReference] = None
    ) -> int:
        if list_ is None:
            list_ = self.content_references
        result = len(
            [ref for ref in list_ if ref.raw_reference and ref.raw_reference.url_found]
        )
        return result

    # def number_of_content_references_with_wm_link(
    #     self, list_: List[WikipediaReference] = None
    # ) -> int:
    #     if list_ is None:
    #         list_ = self.content_references
    #     result = len(
    #         [
    #             ref
    #             for ref in list_
    #             if ref.raw_reference and ref.raw_reference.web_archive_org_in_reference
    #         ]
    #     )
    #     return result

    # def number_of_content_references_with_ia_details_link(
    #     self, list_: List[WikipediaReference] = None
    # ) -> int:
    #     if list_ is None:
    #         list_ = self.content_references
    #     result = len(
    #         [
    #             ref
    #             for ref in list_
    #             if ref.raw_reference
    #             and ref.raw_reference.archive_org_slash_details_in_reference
    #         ]
    #     )
    #     return result

    def __extract_all_raw_citation_references__(self):
        """This extracts everything inside <ref></ref> tags"""
        from src.models.api import app

        app.logger.debug("__extract_all_raw_citation_references__: running")
        # Thanks to https://github.com/JJMC89,
        # see https://github.com/earwig/mwparserfromhell/discussions/295#discussioncomment-4392452
        self.__parse_wikitext__()
        # tag = Tag
        # tag.tag
        refs = self.wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
        app.logger.debug(f"Number of refs found: {len(refs)}")
        for ref in refs:
            self.raw_references.append(
                WikipediaRawReference(
                    wikicode=ref,
                    # wikibase=self.wikibase,
                    testing=self.testing,
                    check_urls=self.check_urls,
                    language_code=self.language_code,
                )
            )

    def __extract_all_raw_general_references__(self):
        """This extracts everything inside <ref></ref> tags"""
        from src.models.api import app

        app.logger.debug("__extract_all_raw_general_references__: running")
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
                    # We discard all lines not starting with a star to avoid all
                    # categories and other templates not containing any references
                    if self.star_found_at_line_start(line=line):
                        parsed_line = mwparserfromhell.parse(line)
                        logger.debug("Appending line with star to self.raw_references")
                        # We don't know what the line contains so we assume it is a reference
                        self.raw_references.append(
                            WikipediaRawReference(
                                wikicode=parsed_line,
                                # wikibase=self.wikibase,
                                testing=self.testing,
                                is_general_reference=True,
                            )
                        )

    def extract_all_references(self):
        """Extract all references from self.wikitext"""
        from src.models.api import app

        app.logger.debug("extract_all_references: running")
        self.__parse_wikitext__()
        self.__extract_all_raw_citation_references__()
        self.__extract_all_raw_general_references__()
        self.__extract_and_check_urls_on_references__()
        self.__convert_raw_references_to_reference_objects__()
        # self.__get_checked_and_unique_reference_urls_from_references__()

    def __convert_raw_references_to_reference_objects__(self):
        from src.models.api import app

        app.logger.debug("__convert_raw_references_to_reference_objects__: running")
        self.references = [
            raw_reference.get_finished_wikipedia_reference_object()
            for raw_reference in self.raw_references
        ]

    def __extract_and_check_urls_on_references__(self):
        from src.models.api import app

        app.logger.debug("__extract_and_check_urls_on_raw_references__: running")
        for reference in self.references:
            if not reference.raw_reference:
                raise MissingInformationError("no raw_reference")
            reference.raw_reference.extract_and_check()
        self.check_urls_done = True

    def __extract_sections__(self):
        from src.models.api import app

        app.logger.debug("__extract_sections__: running")
        if not self.wikicode:
            self.__parse_wikitext__()
        # TODO rewrite to return a dictionary with the section name as key and the data as value
        self.sections: List[Wikicode] = self.wikicode.get_sections(
            levels=[2],
            matches="bibliography|further reading|works cited|sources|external links",
            flags=re.I,
            include_headings=False,
        )
        app.logger.debug(f"Number of sections found: {len(self.sections)}")

    def __parse_wikitext__(self):
        from src.models.api import app

        app.logger.debug("__parse_wikitext__: running")
        if not self.wikicode:
            self.wikicode = mwparserfromhell.parse(self.wikitext)

    @property
    def reference_ids(self) -> List[str]:
        ids = []
        for reference in self.references:
            ids.append(reference.reference_id)
        return ids

    @staticmethod
    def star_found_at_line_start(line) -> bool:
        """This determines if the line in the current section has a star"""
        return bool("*" in line[:1])
