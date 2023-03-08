"""
Copyright Dennis Priskorn where not stated otherwise
"""
import logging
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import mwparserfromhell  # type: ignore
from mwparserfromhell.nodes import ExternalLink, Tag  # type: ignore
from mwparserfromhell.wikicode import Wikicode  # type: ignore

import config
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.reference.enums import (
    FootnoteSubtype,
    ReferenceType,
)
from src.models.wikimedia.wikipedia.reference.template.template import WikipediaTemplate
from src.models.wikimedia.wikipedia.url import WikipediaUrl
from src.wcd_base_model import WcdBaseModel

if TYPE_CHECKING:
    from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference

logger = logging.getLogger(__name__)


# TODO this does not scale at all if we want multi-wiki support :/
class WikipediaRawReference(WcdBaseModel):
    """This class handles determining the type of reference and parse the templates from the raw reference

    This contains code from pywikibot 7.2.0 textlib.py to avoid forking the whole thing
    """

    wikicode: Union[Tag, Wikicode]  # output from mwparserfromhell
    templates: List[WikipediaTemplate] = []
    multiple_templates_found: bool = False
    testing: bool = False
    # wikibase: Wikibase
    extraction_done: bool = False
    is_empty_named_reference: bool = False
    is_general_reference: bool = False
    check_urls_done: bool = False
    checked_urls: List[WikipediaUrl] = []
    check_urls: bool = False
    wikicoded_links: List[WikipediaUrl] = []
    wikicoded_links_done: bool = False
    bare_urls: List[WikipediaUrl] = []
    bare_urls_done: bool = False
    template_urls: List[WikipediaUrl] = []
    template_urls_done: bool = False
    reference_urls: List[WikipediaUrl] = []
    reference_urls_done: bool = False
    first_level_domains: List[str] = []
    first_level_domains_done = True
    language_code: str = ""

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    # @property
    # def has_wm_link(self) -> bool:
    #     return bool([url for url in self.urls if url.is_wayback_machine_url()])

    @property
    def reference_type(self) -> Optional[ReferenceType]:
        if self.is_general_reference:
            type_ = ReferenceType.GENERAL
        elif self.is_footnote_reference:
            type_ = ReferenceType.FOOTNOTE
        else:
            logger.error("Could not determine type")
            type_ = None
        return type_

    @property
    def footnote_subtype(self) -> Optional[FootnoteSubtype]:
        type_ = None
        if self.is_footnote_reference:
            if self.is_empty_named_reference:
                type_ = FootnoteSubtype.NAMED
            else:
                type_ = FootnoteSubtype.CONTENT
        return type_

    @property
    def titles(self) -> List[str]:
        titles = []
        for template in self.templates:
            if template.parameters and "title" in template.parameters:
                titles.append(template.parameters["title"])
        return titles

    # @property
    # def identifiers(self) -> Dict[str, List[str]]:
    #     """Convenience method for patrons. We support DOI and ISBN"""
    #     dois = []
    #     isbns = []
    #     identifiers = {}
    #     for template in self.templates:
    #         if template.parameters:
    #             # for now we only support two
    #             if "doi" in template.parameters:
    #                 dois.append(template.parameters["doi"])
    #             if "isbn" in template.parameters:
    #                 isbns.append(template.parameters["isbn"])
    #     identifiers["dois"] = dois
    #     identifiers["isbns"] = isbns
    #     return identifiers

    @property
    def get_template_dicts(self) -> List[Dict[str, Any]]:
        template_dicts = []
        for template in self.templates:
            template_dicts.append(template.get_dict())
        return template_dicts

    @property
    def template_names(self) -> List[str]:
        template_names = []
        for template in self.templates:
            template_names.append(template.name)
        return template_names

    # @property
    # def multiple_cs1_templates_found(self):
    #     """Detect a ref with multiple CS1 templates like so:
    #             <ref name="territory">*{{Cite web|last=Benedikter|
    #     first=Thomas|date=19 June 2006|title=The working autonomies in Europe|url=http://www.gfbv.it/3dossier/eu-min/autonomy.html|publisher=[[
    #     Society for Threatened Peoples]]|quote=Denmark has established very specific territorial autonomies with its two island territories|acc
    #     ess-date=8 June 2012|archive-date=9 March 2008|archive-url=https://web.archive.org/web/20080309063149/http://www.gfbv.it/3dossier/eu-mi
    #     n/autonomy.html|url-status=dead}}
    #     *{{Cite web|last=Ackrén|first=Maria|date=November 2017|title=Greenland|url=http://www.world-autonomies.info/tas/Greenland/Pages/default
    #     .aspx|url-status=dead|archive-url=https://web.archive.org/web/20190830110832/http://www.world-autonomies.info/tas/Greenland/Pages/defau
    #     lt.aspx|archive-date=30 August 2019|access-date=30 August 2019|publisher=Autonomy Arrangements in the World|quote=Faroese and Greenland
    #     ic are seen as official regional languages in the self-governing territories belonging to Denmark.}}
    #     *{{Cite web|date=3 June 2013|title=Greenland|url=https://ec.europa.eu/europeaid/countries/greenland_en|access-date=27
    #     August 2019|website=International Cooperation and Development|publisher=[[European Commission]]|
    #     language=en|quote=Greenland [...]
    #     is an autonomous territory within the Kingdom of Denmark}}</ref>"""
    #     return bool(self.number_of_cs1_templates > 1)
    #
    # @property
    # def number_of_cs1_templates(self):
    #     return len(
    #         [template for template in self.templates if template.is_cs1_template]
    #     )
    #
    # @property
    # def number_of_bareurl_templates(self):
    #     return len(
    #         [template for template in self.templates if template.is_bareurl_template]
    #     )
    #
    # @property
    # def number_of_citation_templates(self):
    #     return len(
    #         [template for template in self.templates if template.is_citation_template]
    #     )
    #
    # @property
    # def number_of_citeq_templates(self):
    #     return len(
    #         [template for template in self.templates if template.is_citeq_template]
    #     )
    #
    # @property
    # def number_of_isbn_templates(self):
    #     return len(
    #         [template for template in self.templates if template.is_isbn_template]
    #     )
    #
    # @property
    # def number_of_webarchive_templates(self):
    #     return len(
    #         [template for template in self.templates if template.is_webarchive_template]
    #     )
    #
    # @property
    # def known_multiref_template_found(self):
    #     return bool(
    #         [
    #             template
    #             for template in self.templates
    #             if template.is_known_multiref_template
    #         ]
    #     )

    # @property
    # def multiple_url_templates_found(self):
    #     """Detect a ref with multiple url templates"""
    #     return bool(self.number_of_url_templates > 1)

    # @property
    # def number_of_url_templates(self):
    #     return len(
    #         [template for template in self.templates if template.is_url_template]
    #     )

    @property
    def raw_urls(self) -> List[str]:
        """Get a list of the raw urls"""
        urls = []
        for url in self.reference_urls:
            urls.append(url.url)
        return urls

    @property
    def common_url_scheme_found(self) -> bool:
        """Simple, quick and inexpensive search for valid URLs with a common scheme
        This should catch >95% of all URLs in Wikipedia references"""
        return bool("http://" or "https://" or "ftp://" in self.get_wikicode_as_string)

    @property
    def url_found(self) -> bool:
        # first try inexpensive ones
        if self.common_url_scheme_found:
            return True
        elif not self.bare_urls_done:
            self.__extract_bare_urls__()
            return bool(self.bare_urls)
        elif not self.wikicoded_links_done:
            self.__extract_external_wikicoded_links_from_the_reference__()
            return bool(self.wikicoded_links)
        elif not self.template_urls_done:
            self.__extract_template_urls__()
            return bool(self.template_urls)
        else:
            return False

    @property
    def get_stripped_wikicode(self):
        if isinstance(self.wikicode, Wikicode):
            return self.wikicode.strip_code()
        else:
            # support Tag
            return self.wikicode.contents.strip_code()

    def __extract_template_urls__(self) -> None:
        urls = list()
        for template in self.templates:
            if template.urls:
                urls.extend(template.urls)
        self.template_urls = list(urls)
        self.template_urls_done = True

    def __extract_bare_urls__(self) -> None:
        """This is a slightly more sophisticated and slower search for bare URLs using a regex"""
        urls = list()
        for url in self.__find_bare_urls__():
            # We get a tuple back so we join it
            urls.append(WikipediaUrl(url="".join(url)))
        self.bare_urls = urls
        self.bare_urls_done = True

    def __extract_external_wikicoded_links_from_the_reference__(self) -> None:
        """This relies on mwparserfromhell to find links like [google.com Google] in the wikitext"""
        urls = set()
        if isinstance(self.wikicode, Wikicode):
            for url in self.wikicode.ifilter_external_links():
                # url: ExternalLink
                # we throw away the title here
                urls.add(WikipediaUrl(url=str(url.url)))
        else:
            for url in self.wikicode.contents.ifilter_external_links():
                # url: ExternalLink
                # we throw away the title here
                urls.add(WikipediaUrl(url=str(url.url)))
        self.wikicoded_links = list(urls)
        self.wikicoded_links_done = True

    def __extract_reference_urls__(self) -> None:
        """We support both URLs in templates and outside aka bare URLs"""
        urls_list = list()
        if not self.template_urls_done:
            self.__extract_template_urls__()
        urls_list.extend(self.template_urls)
        if not self.bare_urls_done:
            self.__extract_bare_urls__()
        urls_list.extend(self.bare_urls)
        if not self.wikicoded_links_done:
            self.__extract_external_wikicoded_links_from_the_reference__()
        urls_list.extend(self.wikicoded_links)
        # We set it to avoid duplicates
        self.reference_urls = list(set(urls_list))
        self.reference_urls_done = True

    def __extract_first_level_domains__(self) -> None:
        """This aggregates all first level domains from the urls found in the raw references"""
        logger.debug("__extract_first_level_domains__: running")
        if not self.reference_urls_done:
            raise MissingInformationError("reference_urls have not been extracted")
        if self.reference_urls:
            logger.debug("found at least one url")
            for url in self.reference_urls:
                logger.debug("working on url")
                if not url.first_level_domain_done:
                    url.extract_first_level_domain()
                if url.first_level_domain:
                    logger.debug(f"found fld: {url.first_level_domain}")
                    self.first_level_domains.append(url.first_level_domain)
        logger.debug(f"found flds: {self.first_level_domains}")
        self.first_level_domains_done = True

    # @property
    # def google_books_template_found(self):
    #     """Google books templates look like this:
    #     {{google books |plainurl=y |id=CDJpAAAAMAAJ |page=313}}"""
    #     for template in self.templates:
    #         if "google books" == template.name:
    #             return True
    #     return False

    # @property
    # def google_books_url_or_template_found(self):
    #     """This detects both google book templates and google books url
    #     example: https://books.google.se/books?id=9HRodACJLOoC&printsec=
    #     frontcover&dq=test&hl=sv&sa=X&redir_esc=y#v=onepage&q=test&f=false"""
    #     return bool(
    #         bool("//books.google." in self.get_wikicode_as_string)
    #         or self.google_books_template_found
    #     )

    # @property
    # def web_archive_org_in_reference(self):
    #     return bool("web.archive.org" in self.get_wikicode_as_string)
    #
    # @property
    # def archive_org_slash_details_in_reference(self):
    #     return bool("archive.org/details" in self.get_wikicode_as_string)

    @property
    def plain_text_in_reference(self) -> bool:
        # Try removing everything that is inside templates markup and see if anything is left
        if isinstance(self.wikicode, Tag):
            stripped_wikicode = self.wikicode.contents.strip_code().strip()
        else:
            stripped_wikicode = self.wikicode.strip_code().strip()
        logger.debug(f"Stripped wikicode: '{stripped_wikicode}'")
        if len(stripped_wikicode) == 0:
            return False
        else:
            return True

    # @property
    # def cite_book_template_found(self) -> bool:
    #     return self.specific_template_found(names="cite book")
    #
    # @property
    # def cite_journal_template_found(self) -> bool:
    #     return self.specific_template_found(names="cite journal")
    #
    # @property
    # def cite_web_template_found(self) -> bool:
    #     return self.specific_template_found(names="cite web")
    #
    # @property
    # def citation_template_found(self) -> bool:
    #     return self.specific_template_found(names=config.citation_template)
    #
    # @property
    # def deprecated_reference_template_found(self):
    #     for template in self.templates:
    #         if template.name in config.deprecated_templates:
    #             return True
    #     return False
    #
    # @property
    # def cs1_template_found(self) -> bool:
    #     """This searches for at least one CS1 templates"""
    #     for template in self.templates:
    #         if template.is_cs1_template:
    #             return True
    #     return False
    #
    # @property
    # def citeq_template_found(self) -> bool:
    #     for template in self.templates:
    #         if template.name in config.citeq_templates:
    #             return True
    #     return False
    #
    # @property
    # def isbn_template_found(self) -> bool:
    #     return self.specific_template_found(names=config.isbn_template)
    #
    # @property
    # def url_template_found(self) -> bool:
    #     return self.specific_template_found(names=config.url_template)

    @property
    def bare_url_template_found(self) -> bool:
        for template in self.templates:
            if config.bare_url_regex in template.name:
                return True
        return False

    @property
    def is_footnote_reference(self):
        """This could also be implemented based on the class type of the wikicode attribute.
        I choose not to because it could perhaps be brittle."""
        if self.is_general_reference:
            return False
        else:
            return True

    @property
    def get_wikicode_as_string(self):
        return str(self.wikicode)

    @property
    def number_of_templates(self) -> int:
        return len(self.templates)

    # @property
    # def number_of_templates_missing_first_parameter(self) -> int:
    #     """This parameter is needed for some templates"""
    #     if self.number_of_templates:
    #         return len(
    #             [
    #                 template
    #                 for template in self.templates
    #                 if template.missing_or_empty_first_parameter
    #             ]
    #         )
    #     else:
    #         return 0

    def __find_bare_urls__(self, stripped_wikicode: str = "") -> List[tuple]:
        """Return bare urls from the stripped wikitext"""
        if not stripped_wikicode:
            stripped_wikicode = self.get_stripped_wikicode
        return re.findall(
            r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?",
            stripped_wikicode,
        )

    # def __found_template__(self, name: str = "") -> bool:
    #     for template in self.templates:
    #         if name == template.name:
    #             return True
    #     return False

    # def __check_urls__(self):
    #     """This checks the status of all the URLs"""
    #     logger.debug("__check_urls__: running")
    #     if not self.extraction_done:
    #         raise MissingInformationError("extraction not done")
    #     if not self.reference_urls_done:
    #         raise MissingInformationError("reference_urls not done")
    #     for url in self.reference_urls:
    #         url.extract()
    #         self.checked_urls.append(url)
    #     self.check_urls_done = True
    #
    # def specific_template_found(self, names: Union[str, List[str]] = "") -> bool:
    #     """Used to search one instance of a specific templates"""
    #     if isinstance(names, list):
    #         for name in names:
    #             return self.__found_template__(name=name)
    #     else:
    #         return self.__found_template__(name=names)
    #     return False

    def __extract_templates_and_parameters__(self) -> None:
        """Helper method"""
        logger.debug("__extract_templates_and_parameters_from_raw_reference__: running")
        self.__extract_raw_templates__()
        self.__extract_and_clean_template_parameters__()
        self.extraction_done = True

    def __extract_raw_templates__(self) -> None:
        """Extract the templates from self.wikicode"""
        logger.debug("__extract_raw_templates__: running")
        if not self.wikicode:
            raise MissingInformationError("self.wikicode was None")
        if isinstance(self.wikicode, str):
            raise MissingInformationError("self.wikicode was str")
        # Skip named references like "<ref name="INE"/>"
        wikicode_string = str(self.wikicode)
        if self.is_footnote_reference and (
            "</ref>" not in wikicode_string or "></ref>" in wikicode_string
        ):
            logger.info(f"Skipping named reference with no content {wikicode_string}")
            self.is_empty_named_reference = True
        else:
            logger.debug(f"Extracting templates from: {self.wikicode}")
            if isinstance(self.wikicode, Tag):
                # contents is needed here to get a Wikicode object
                raw_templates = self.wikicode.contents.ifilter_templates(
                    matches=lambda x: not x.name.lstrip().startswith("#"),
                    recursive=True,
                )
            else:
                raw_templates = self.wikicode.ifilter_templates(
                    matches=lambda x: not x.name.lstrip().startswith("#"),
                    recursive=True,
                )
            count = 0
            for raw_template in raw_templates:
                count += 1
                self.templates.append(
                    WikipediaTemplate(
                        raw_template=raw_template, language_code=self.language_code
                    )
                )
            if count == 0:
                logger.debug(f"Found no templates in {self.wikicode}")

    def __extract_and_clean_template_parameters__(self) -> None:
        """We only extract and clean if exactly one templates is found"""
        logger.debug("__extract_and_clean_template_parameters__: running")
        if self.number_of_templates == 1:
            [
                template.extract_and_prepare_parameter_and_flds()
                for template in self.templates
            ]
            for template in self.templates:
                if not template.extraction_done:
                    raise ValueError()

    def extract_and_check(self) -> None:
        """Helper method"""
        logger.debug("extract_and_check: running")
        self.__extract_templates_and_parameters__()
        # self.__determine_if_multiple_templates__()
        self.__extract_reference_urls__()
        self.__extract_first_level_domains__()
        # if self.check_urls:
        #     self.__check_urls__()
        # else:
        #     logger.info("Not checking urls for this raw reference")

    def get_finished_wikipedia_reference_object(self) -> "WikipediaReference":
        """Make a WikipediaReference based on the extracted information"""
        logger.debug("get_finished_wikipedia_reference_object: running")
        if not self.extraction_done:
            self.extract_and_check()
        from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference

        if self.number_of_templates:
            reference = WikipediaReference(**self.templates[0].parameters)
        else:
            reference = WikipediaReference()
        # propagate attributes
        reference.raw_reference = self
        reference.cache = self.cache
        # reference.wikibase = self.wikibase
        reference.finish_parsing_and_generate_hash(testing=self.testing)
        return reference

    # def __determine_if_multiple_templates__(self):
    #     """We want to determine which type of reference this is
    #
    #     Design limit: we only support one templates for now"""
    #     if self.number_of_templates:
    #         logger.info(
    #             f"Found {self.number_of_templates} templates(s) in {self.wikicode}"
    #         )
    #         if self.number_of_templates > 1:
    #             self.multiple_templates_found = True
    #             message = (
    #                 f"We found {self.number_of_templates} templates in "
    #                 f"{self.wikicode} -> templates: {self.templates} which is currently not supported"
    #             )
    #             logger.error(message)
    #             self.__log_to_file__(
    #                 message=message, file_name="multiple_template_error.log"
    #             )
    #
