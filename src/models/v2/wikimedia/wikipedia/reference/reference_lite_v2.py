import hashlib
import logging
import re
from typing import Any, Dict, List, Optional, Union

from bs4 import BeautifulSoup, Comment
from mwparserfromhell.nodes import Tag  # type: ignore
from mwparserfromhell.wikicode import Wikicode  # type: ignore

from config import regex_url_link_extraction
from src.models.base.job import JobBaseModel
from src.models.exceptions import MissingInformationError
from src.models.v2.wikimedia.wikipedia.reference.template import WikipediaTemplateV2
from src.models.v2.wikimedia.wikipedia.url_v2 import WikipediaUrlV2
from src.models.wikimedia.wikipedia.reference.enums import (
    FootnoteSubtype,
    ReferenceType,
)

logger = logging.getLogger(__name__)


# We use marshmallow here because pydantic did not seem to support optional alias fields.
# https://github.com/samuelcolvin/pydantic/discussions/3855


class WikipediaReferenceLiteV2(JobBaseModel):
    """
    models a reference on a Wikipedia page
    See class WikipediaReferenceV2(JobBaseModel) for what this was based on

    This is very simple for now. we just have a name (of the reference, if there) and wikitext

    we validate with pydantic when creating this object
    """

    wikicode: Union[Tag, Wikicode]  # output from mwparserfromhell

    name: str = ""
    wikitext: str = ""

    # This is for pydantic
    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    @property
    def get_name(self) -> str:
        if not self.soup:
            raise MissingInformationError()
        # Find the <ref> tag
        ref_tag = self.soup.find("ref")
        if ref_tag:
            # Extract the value of the 'name' attribute
            name = str(ref_tag.get("name"))  # type: ignore # see https://github.com/python/typeshed/issues/8356
            if name.endswith("\\"):
                # Cut off the trailing backward slash
                name = name[:-1]
            if name.endswith("/"):
                # Cut off the trailing forward slash
                name = name[:-1]
            if name == "None" or name is None:
                return ""
            else:
                return name
        else:
            return ""


    @property
    def wikicode_as_string(self):
        return str(self.wikicode)

    def __parse_xhtml__(self):
        self.soup = BeautifulSoup(str(self.wikicode), "lxml")

    def __extract_template_urls__(self) -> None:
        self.template_urls = []
        urls = []
        if self.templates:
            for template in self.templates:
                if template.urls:
                    urls.extend(template.urls)
        self.template_urls = urls

    def __extract_bare_urls_outside_templates__(self) -> None:
        """This is a slightly more sophisticated and slower search for bare URLs using a regex"""
        self.bare_urls = []
        urls = []
        for url in self.__find_bare_urls_outside_templates__():
            url_object = WikipediaUrlV2(url=url)
            url_object.extract()
            urls.append(url_object)
        self.bare_urls = urls

    # def __extract_external_wikicoded_links_from_the_reference__(self) -> None:
    #     """
    #     Uses mwparserfromhell's ifilter_external_links function (via wikicode.ifilter_external_links)
    #     returns iterator of external links found in the wikicode, like [google.com Google]
    #     """
    #     self.wikicoded_links = []
    #     urls = set()
    #
    #     # Check if self.wikicode is an instance of Wikicode
    #     if isinstance(self.wikicode, Wikicode):
    #         # Get external links directly from self.wikicode
    #         links = self.wikicode.ifilter_external_links()
    #     else:
    #         # Get external links from the contents of self.wikicode
    #         links = self.wikicode.contents.ifilter_external_links()
    #
    #     for url in links:
    #         # url: ExternalLink
    #         # we throw away the title here
    #         url = WikipediaUrlV2(url=str(url.url))
    #         url.extract()
    #         urls.add(url)
    #
    #     self.wikicoded_links = list(urls)

    # def __extract_reference_urls__(self) -> None:
    #     """We support both URLs in templates and outside aka bare URLs"""
    #     urls_list = []
    #
    #     if not self.template_urls:
    #         self.__extract_template_urls__()
    #     if self.template_urls:
    #         urls_list.extend(self.template_urls)
    #
    #     if not self.bare_urls:
    #         self.__extract_bare_urls_outside_templates__()
    #     if self.bare_urls:
    #         urls_list.extend(self.bare_urls)
    #
    #     if not self.wikicoded_links:
    #         self.__extract_external_wikicoded_links_from_the_reference__()
    #     if self.wikicoded_links:
    #         urls_list.extend(self.wikicoded_links)
    #
    #     # if not self.comment_urls:
    #     #     self.__extract_urls_from_comments__()
    #     # urls_list.extend(self.comment_urls)
    #     # We set it to avoid duplicates
    #
    #     self.reference_urls = list(set(urls_list))
    #
    # def __extract_unique_first_level_domains__(self) -> None:
    #     """This aggregates all first level domains from the urls found in the urls"""
    #     from src import app
    #
    #     app.logger.debug("__extract_first_level_domains__: running")
    #     if not self.reference_urls:
    #         app.logger.info("no reference_urls found so we skip extraction")
    #     else:
    #         logger.debug("found at least one url")
    #         first_level_domains = set()
    #         for url in self.reference_urls:
    #             logger.debug("working on url")
    #             if url.first_level_domain:
    #                 app.logger.debug(f"found fld: {url.first_level_domain}")
    #                 first_level_domains.add(url.first_level_domain)
    #             else:
    #                 app.logger.warning(f"no fld found for: {url.url}")
    #         # Return unique domains to avoid confusion
    #         # https://github.com/internetarchive/iari/issues/834
    #         self.unique_first_level_domains = list(first_level_domains)
    #         app.logger.debug(f"found unique flds: {self.unique_first_level_domains}")


    # def __find_bare_urls_outside_templates__(self) -> List[str]:
    #     """Return bare urls from the the stripped wikitext (templates are stripped away)"""
    #     if isinstance(self.wikicode, Wikicode):
    #         stripped_wikicode = str(self.wikicode.strip_code())
    #         logger.debug(stripped_wikicode)
    #         return re.findall(
    #             regex_url_link_extraction,
    #             stripped_wikicode,
    #         )
    #     else:
    #         return []

    #
    # def __extract_templates_and_parameters__(self) -> None:
    #     """Helper method"""
    #     from src import app
    #
    #     app.logger.debug(
    #         "__extract_templates_and_parameters_from_raw_reference__: running"
    #     )
    #     self.__extract_raw_templates__()
    #     self.__extract_and_clean_template_parameters__()
    #     self.extraction_done = True

    # def __extract_raw_templates__(self) -> None:
    #     """Extract the templates from self.wikicode"""
    #     from src import app
    #
    #     self.templates = []
    #     app.logger.debug("__extract_raw_templates__: running")
    #     if not self.wikicode:
    #         raise MissingInformationError("self.wikicode was None")
    #     if isinstance(self.wikicode, str):
    #         raise MissingInformationError("self.wikicode was str")
    #     # Skip named references like "<ref name="INE"/>"
    #     wikicode_string = str(self.wikicode)
    #     if self.is_footnote_reference and (
    #         "</ref>" not in wikicode_string or "></ref>" in wikicode_string
    #     ):
    #         logger.info(f"Skipping named reference with no content {wikicode_string}")
    #         self.is_named_reused_reference = True
    #     else:
    #         logger.debug(f"Extracting templates from: {self.wikicode}")
    #         if isinstance(self.wikicode, Tag):
    #             # contents is needed here to get a Wikicode object
    #             raw_templates = self.wikicode.contents.ifilter_templates(
    #                 matches=lambda x: not x.name.lstrip().startswith("#"),
    #                 recursive=True,
    #             )
    #         else:
    #             raw_templates = self.wikicode.ifilter_templates(
    #                 matches=lambda x: not x.name.lstrip().startswith("#"),
    #                 recursive=True,
    #             )
    #         count = 0
    #         for raw_template in raw_templates:
    #             count += 1
    #             self.templates.append(
    #                 WikipediaTemplate(
    #                     raw_template=raw_template, language_code=self.language_code
    #                 )
    #             )
    #         if count == 0:
    #             logger.debug("Found no templates")

    # def __extract_and_clean_template_parameters__(self) -> None:
    #     """We extract all templates"""
    #     from src import app
    #
    #     app.logger.debug("__extract_and_clean_template_parameters__: running")
    #     if self.templates:
    #         [
    #             template.extract_and_prepare_parameter_and_flds()
    #             for template in self.templates
    #         ]

    def extract_and_check(self) -> None:
        """Helper method"""
        from src import app

        app.logger.debug("extract_and_check: running")
        self.__parse_xhtml__()
        # self.__extract_xhtml_comments__()
        # self.__extract_templates_and_parameters__()
        # self.__extract_reference_urls__()
        # self.__extract_unique_first_level_domains__()
        # self.__generate_reference_id__()

    # def extract_and_check(self) -> None:
    #     """Helper method"""
    #     from src import app
    #
    #     app.logger.debug("extract_and_check: running")
    #     self.__parse_xhtml__()
    #     self.__extract_xhtml_comments__()
    #     self.__extract_templates_and_parameters__()
    #     self.__extract_reference_urls__()
    #     self.__extract_unique_first_level_domains__()
    #     self.__generate_reference_id__()

    def __generate_reference_id__(self) -> None:
        """This generates an 8-char long id based on the md5 hash of
        the raw wikitext for this reference"""
        self.reference_id = hashlib.md5(f"{self.wikicode}".encode()).hexdigest()[:8]

