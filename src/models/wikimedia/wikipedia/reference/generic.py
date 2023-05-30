import hashlib
import logging
import re
from typing import Any, Dict, List, Optional, Union

from bs4 import BeautifulSoup
from mwparserfromhell.nodes import Tag  # type: ignore
from mwparserfromhell.wikicode import Wikicode  # type: ignore

from config import link_extraction_regex
from src.models.base.job import JobBaseModel
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.reference.enums import (
    FootnoteSubtype,
    ReferenceType,
)
from src.models.wikimedia.wikipedia.reference.template.template import WikipediaTemplate
from src.models.wikimedia.wikipedia.url import WikipediaUrl

logger = logging.getLogger(__name__)


# We use marshmallow here because pydantic did not seem to support optional alias fields.
# https://github.com/samuelcolvin/pydantic/discussions/3855


class WikipediaReference(JobBaseModel):
    """This models any page_reference on a Wikipedia page

    As we move to support more than one Wikipedia this model should be generalized further.

    Do we want to merge page + pages into a string property like in Wikidata?
    How do we handle parse errors? In a file log? Should we publish the log for Wikipedians to fix?

    Validation works better with pydantic so we validate when creating this object

    Support date ranges like "May-June 2011"? See https://stackoverflow.com/questions/10340029/
    """

    wikicode: Union[Tag, Wikicode]  # output from mwparserfromhell
    templates: List[WikipediaTemplate] = []
    multiple_templates_found: bool = False
    testing: bool = False
    extraction_done: bool = False
    is_empty_named_reference: bool = False
    is_general_reference: bool = False
    wikicoded_links: List[WikipediaUrl] = []
    bare_urls: List[WikipediaUrl] = []
    template_urls: List[WikipediaUrl] = []
    reference_urls: List[WikipediaUrl] = []
    unique_first_level_domains: List[str] = []
    language_code: str = ""
    reference_id: str = ""
    section: str

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    @property
    def get_name(self) -> str:
        soup = BeautifulSoup(str(self.wikicode), "lxml")
        # Find the <ref> tag
        ref_tag = soup.find("ref")
        if ref_tag:
            # Extract the value of the 'name' attribute
            name = ref_tag.get("name")  # type: ignore # see https://github.com/python/typeshed/issues/8356
            return name if isinstance(name, str) else ""
        else:
            return ""

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
            type_ = (
                FootnoteSubtype.NAMED
                if self.is_empty_named_reference
                else FootnoteSubtype.CONTENT
            )
        return type_

    @property
    def titles(self) -> List[str]:
        titles = []
        for template in self.templates:
            if template.parameters and "title" in template.parameters:
                titles.append(template.parameters["title"])
        return titles

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

    @property
    def raw_urls(self) -> List[str]:
        """Get a list of the raw unique urls"""
        urls = []
        for url in self.reference_urls:
            urls.append(url.url)
        return urls

    def __extract_template_urls__(self) -> None:
        urls = []
        for template in self.templates:
            if template.urls:
                urls.extend(template.urls)
        self.template_urls = list(urls)

    def __extract_bare_urls__(self) -> None:
        """This is a slightly more sophisticated and slower search for bare URLs using a regex"""
        urls = []
        for url in self.__find_bare_urls__():
            url_object = WikipediaUrl(url=url)
            url_object.extract()
            urls.append(url_object)
        self.bare_urls = urls

    def __extract_external_wikicoded_links_from_the_reference__(self) -> None:
        """This relies on mwparserfromhell to find links like [google.com Google] in the wikitext"""
        urls = set()
        if isinstance(self.wikicode, Wikicode):
            for url in self.wikicode.ifilter_external_links():
                # url: ExternalLink
                # we throw away the title here
                url = WikipediaUrl(url=str(url.url))
                url.extract()
                urls.add(url)
        else:
            for url in self.wikicode.contents.ifilter_external_links():
                # url: ExternalLink
                # we throw away the title here
                url = WikipediaUrl(url=str(url.url))
                url.extract()
                urls.add(url)
        self.wikicoded_links = list(urls)

    def __extract_reference_urls__(self) -> None:
        """We support both URLs in templates and outside aka bare URLs"""
        urls_list = []
        if not self.template_urls:
            self.__extract_template_urls__()
        urls_list.extend(self.template_urls)
        if not self.bare_urls:
            self.__extract_bare_urls__()
        urls_list.extend(self.bare_urls)
        if not self.wikicoded_links:
            self.__extract_external_wikicoded_links_from_the_reference__()
        urls_list.extend(self.wikicoded_links)
        # We set it to avoid duplicates
        self.reference_urls = list(set(urls_list))

    def __extract_unique_first_level_domains__(self) -> None:
        """This aggregates all first level domains from the urls found in the urls"""
        from src import app

        app.logger.debug("__extract_first_level_domains__: running")
        if not self.reference_urls:
            app.logger.info("no reference_urls found so we skip extraction")
        else:
            logger.debug("found at least one url")
            first_level_domains = set()
            for url in self.reference_urls:
                logger.debug("working on url")
                if url.first_level_domain:
                    app.logger.debug(f"found fld: {url.first_level_domain}")
                    first_level_domains.add(url.first_level_domain)
                else:
                    app.logger.warning(f"no fld found for: {url.url}")
            # Return unique domains to avoid confusion
            # https://github.com/internetarchive/iari/issues/834
            self.unique_first_level_domains = list(first_level_domains)
            app.logger.debug(f"found unique flds: {self.unique_first_level_domains}")

    # @property
    # def plain_text_in_reference(self) -> bool:
    #     from src.models.api import app
    #
    #     # Try removing everything that is inside templates markup and see if anything is left
    #     if isinstance(self.wikicode, Tag):
    #         stripped_wikicode = self.wikicode.contents.strip_code().strip()
    #     else:
    #         stripped_wikicode = self.wikicode.strip_code().strip()
    #     app.logger.debug(f"Stripped wikicode: '{stripped_wikicode}'")
    #     if len(stripped_wikicode) == 0:
    #         return False
    #     else:
    #         return True

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
    def number_of_templates(self) -> int:  # dead: disable
        """Convenience method for tests"""
        return len(self.templates)

    def __find_bare_urls__(self) -> List[tuple]:
        """Return bare urls from the the raw wikitext"""
        wikicode = str(self.wikicode)
        # logger.debug(wikicode)
        return re.findall(
            link_extraction_regex,
            wikicode,
        )

    def __extract_templates_and_parameters__(self) -> None:
        """Helper method"""
        from src import app

        app.logger.debug(
            "__extract_templates_and_parameters_from_raw_reference__: running"
        )
        self.__extract_raw_templates__()
        self.__extract_and_clean_template_parameters__()
        self.extraction_done = True

    def __extract_raw_templates__(self) -> None:
        """Extract the templates from self.wikicode"""
        from src import app

        app.logger.debug("__extract_raw_templates__: running")
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
                logger.debug("Found no templates")

    def __extract_and_clean_template_parameters__(self) -> None:
        """We extract all templates"""
        from src import app

        app.logger.debug("__extract_and_clean_template_parameters__: running")
        [
            template.extract_and_prepare_parameter_and_flds()
            for template in self.templates
        ]

    def extract_and_check(self) -> None:
        """Helper method"""
        from src import app

        app.logger.debug("extract_and_check: running")
        self.__extract_templates_and_parameters__()
        self.__extract_reference_urls__()
        self.__extract_unique_first_level_domains__()
        self.__generate_reference_id__()

    def __generate_reference_id__(self) -> None:
        """This generates an 8-char long id based on the md5 hash of
        the raw wikitext for this reference"""
        self.reference_id = hashlib.md5(f"{self.wikicode}".encode()).hexdigest()[:8]

    @property
    def get_reference_url_dicts(self) -> List[Dict[str, Any]]:
        urls = []
        if self.reference_urls:
            for url in self.reference_urls:
                urls.append(url.get_dict)
        return urls
