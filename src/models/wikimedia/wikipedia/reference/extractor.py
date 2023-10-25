import logging
from copy import deepcopy
from typing import Any, Dict, List, Optional

import mwparserfromhell  # type: ignore
from bs4 import BeautifulSoup
from mwparserfromhell.wikicode import Wikicode  # type: ignore

from src.models.api.job.article_job import ArticleJob
from src.models.base import WariBaseModel
from src.models.exceptions import MissingInformationError
from src.models.mediawiki.section import MediawikiSection
from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference
from src.models.wikimedia.wikipedia.url import WikipediaUrl

# logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class WikipediaReferenceExtractor(WariBaseModel):
    """This class handles all extraction of references from wikicode

    Design:
    * first we get the wikicode
    * we parse it with mwparser from hell
    * we extract the references -> WikipediaReference
    """

    job: ArticleJob
    language_code: str = ""
    sections: Optional[List[MediawikiSection]] = None

    wikitext: str
    wikicode: Wikicode = None  # wiki object tree parsed from wikitext
    html_source: str = ""  # used to extract citeref reference data

    references: Optional[List[WikipediaReference]] = None
    # cite_page_refs: Optional[List] = []
    cite_page_refs: List = []

    # wikibase: Wikibase # ??? What is this? TODO

    testing: bool = False

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    @property
    def urls(self) -> List[WikipediaUrl]:
        """List of non-unique and valid urls"""
        urls: List[WikipediaUrl] = []

        if self.references:
            for reference in self.references:
                if reference.reference_urls:
                    for url in reference.reference_urls:
                        urls.append(url)
        return urls

    # @property
    # def invalid_urls(self) -> List[WikipediaUrl]:
    #     """List of non-unique and valid urls"""
    #     urls: List[WikipediaUrl] = []
    #     for reference in self.references:
    #         for url in reference.reference_urls:
    #             if not url.valid:
    #                 urls.append(url)
    #     return urls

    @property
    def raw_urls(self) -> List[str]:
        """List of raw non-unique urls found in the reference"""
        urls: List[str] = []
        if self.references:
            for reference in self.references:
                if reference.reference_urls:
                    for url in reference.reference_urls:
                        urls.append(url.url)
        return urls

    @property
    def cite_refs(self) -> Optional[List]:
        return self.cite_page_refs

    @property
    def cite_refs_count(self) -> int:
        return len(self.cite_page_refs)

    @property
    def first_level_domain_counts(self) -> Dict[str, int]:
        """This returns a dict with fld as key and the count as value"""
        fld_set = set(deepcopy(self.first_level_domains))
        counts = {}
        for fld in fld_set:
            count = self.first_level_domains.count(fld)
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
    def first_level_domains(self) -> List[str]:
        """This is a list and duplicates are likely and wanted across the references"""
        if not self.content_references:
            return []
        flds = []
        if self.references:
            for reference in self.references:
                if reference.unique_first_level_domains:
                    flds.extend(reference.unique_first_level_domains)
        return flds

    @property
    def number_of_sections(self) -> int:  # dead: disable
        if not self.sections:
            self.__extract_sections__()
        if self.sections:
            return len(self.sections)
        else:
            return 0

    @property
    def general_references(self):
        return [
            reference
            for reference in self.content_references
            if reference.is_general_reference
        ]

    @property
    def number_of_general_references(self) -> int:
        return len(self.general_references)

    @property
    def footnote_references(self):
        return [
            reference
            for reference in self.content_references
            if reference.is_footnote_reference
        ]

    @property
    def number_of_footnote_references(self) -> int:
        return len(self.footnote_references)

    @property
    def empty_named_references(self):
        """Special type of reference with no content
        Example: <ref name="INE"/>"""
        return [
            reference
            for reference in self.references
            if reference.is_empty_named_reference
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
            if not reference.is_empty_named_reference
        ]

    @property
    def number_of_content_references(self) -> int:
        return len(self.content_references)

    @property
    def number_of_references(self) -> int:
        if self.references:
            return len(self.references)
        else:
            return 0

    # def number_of_content_references_with_a_url(
    #     self, list_: List[WikipediaReference]
    # ) -> int:
    #     if not list_:
    #         list_ = self.content_references
    #     result = len([ref for ref in list_ if ref and ref.url_found])
    #     return result
    #

    # def __extract_all_raw_general_references__(self):
    #     """This extracts everything inside <ref></ref> tags"""
    #     from src import app
    #
    #     app.logger.debug("__extract_all_raw_general_references__: running")
    #     # Thanks to https://github.com/JJMC89,
    #     # see https://github.com/earwig/mwparserfromhell/discussions/295#discussioncomment-4392452
    #     self.__extract_sections__()

    def extract_all_references(self):
        """Extract all references from self.wikitext"""
        from src import app

        app.logger.debug("extract_all_references: running")
        if not self.job:
            raise MissingInformationError("no job")
        self.__parse_wikitext__()
        self.__parse_html_source__()  # fetches html and extracts reference citations
        self.__extract_sections__()
        self.__populate_references__()
        app.logger.info("Done extracting all references")

    def __extract_sections__(self) -> None:
        """This uses the regex supplied by the patron via the API
        and populate the reference_sections attribute with a list of MediawikiSection objects

        We only consider level 2 sections beginning with =="""
        from src import app

        self.sections = []
        app.logger.debug("__extract_sections__: running")
        if not self.wikicode:
            self.__parse_wikitext__()
        sections: List[Wikicode] = self.wikicode.get_sections(
            levels=[2],
            include_headings=True,
        )
        if not sections:
            app.logger.debug("No level 2 sections detected, creating root section")
            # console.print(self.wikicode)
            # exit()
            mw_section = MediawikiSection(
                # We add the whole article to the root section
                wikicode=self.wikicode,
                testing=self.testing,
                language_code=self.language_code,
                job=self.job,
            )
            mw_section.extract()
            self.sections.append(mw_section)
        else:
            self.__extract_root_section__()
            for section in sections:
                mw_section = MediawikiSection(
                    wikicode=section,
                    testing=self.testing,
                    language_code=self.language_code,
                    job=self.job,
                )
                mw_section.extract()
                self.sections.append(mw_section)
        app.logger.debug(f"Number of sections found: {len(self.sections)}")

    def __parse_wikitext__(self):
        from src import app

        app.logger.debug("__parse_wikitext__: running")
        if not self.wikicode:
            self.wikicode = mwparserfromhell.parse(self.wikitext)

    def __extract_cite_refs__(self):

        soup = BeautifulSoup(self.html_source, "html.parser")
        # for link in soup.find_all("a"):
        #     print(link.get("href"))

        references_wrapper = soup.find("div", class_="mw-references-wrap")

        refs = []

        if references_wrapper:
            references_list = references_wrapper.find("ol", class_="references")
            ref_counter = 0
            for ref in references_list.find_all("li"):

                ref_counter += 1

                page_refs = []
                for link in ref.find_all("a"):
                    # span.mw-linkback-text children should have a citeref link
                    if link.find("span", class_="mw-linkback-text"):
                        page_refs.append(
                            {
                                "href": link.get("href"),
                                "id": link.get("id"),
                            }
                        )

                span_link = ref.find("span", class_="mw-reference-text")
                raw_data = None
                if span_link:
                    link_data = span_link.find("link")
                    if link_data:
                        raw_data = link_data.get("data-mw")

                refs.append(
                    {
                        "id": ref.get("id"),
                        "ref_index": ref_counter,
                        "raw_data": raw_data,
                        "page_refs": page_refs,
                    }
                )

        self.cite_page_refs = refs

    def __parse_html_source__(self):
        """
        Parses html to extract cite reference data from references section
        """
        from src import app

        app.logger.debug("__parse_html_source__: running")

        # def is_citeref_link(css_class):
        #     return css_class is None  # and len(css_class) == 6

        if self.html_source:
            self.__extract_cite_refs__()

    @property
    def reference_ids(self) -> List[str]:
        ids = []
        if self.references:
            for reference in self.references:
                ids.append(reference.reference_id)
            return ids
        else:
            return []

    def __populate_references__(self):
        self.references = []
        for section in self.sections:
            for reference in section.references:
                self.references.append(reference)

    def __extract_root_section__(self):
        """This extracts the root section from the beginning until the first level 2 heading"""
        if not self.wikitext:
            raise MissingInformationError()
        self.sections = []
        first_level2_heading_line_number = 0
        for index, line in enumerate(self.wikitext.splitlines()):
            if "==" in line:
                logger.debug(f"found == in line: {line}, with index {index}")
                first_level2_heading_line_number = index
                # We break at first hit
                break
        if first_level2_heading_line_number:
            root_section_wikitext = self.extract_lines(
                end=first_level2_heading_line_number
            )
            # console.print(root_section_wikitext)
            # exit()
            mw_section = MediawikiSection(
                wikitext=root_section_wikitext,
                testing=self.testing,
                language_code=self.language_code,
                job=self.job,
            )
            mw_section.extract()
            self.sections.append(mw_section)
        else:
            logger.debug(
                "Special case, wikitext started with a "
                "level 2 heading so we don't do anything"
            )

    def extract_lines(self, end) -> str:
        """Extract lines until end"""
        lines = ""
        if not end:
            raise MissingInformationError("did not get what we need")
        for index, line in enumerate(str(self.wikicode).splitlines()):
            if index < end:
                lines += f"{line}\n"
        return lines
