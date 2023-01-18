"""
Copyright Dennis Priskorn where not stated otherwise
"""
import logging
import re
from typing import TYPE_CHECKING, List, Set, Union

import mwparserfromhell  # type: ignore
from mwparserfromhell.nodes import Tag  # type: ignore
from mwparserfromhell.wikicode import Wikicode  # type: ignore

import config
from src.models.exceptions import MissingInformationError
from src.models.wikibase import Wikibase
from src.models.wikimedia.wikipedia.reference.template import WikipediaTemplate
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
    wikibase: Wikibase
    extraction_done: bool = False
    is_named_reference: bool = False
    is_general_reference: bool = False
    # TODO add new optional attribute wikicode: Optional[Wikicode]
    #  which contains the parsed output of the general reference line

    class Config:
        arbitrary_types_allowed = True

    @property
    def get_stripped_wikicode(self):
        if isinstance(self.wikicode, Wikicode):
            return self.wikicode.strip_code()
        else:
            # support Tag
            return self.wikicode.contents.strip_code()

    @property
    def __template_urls__(self) -> Set[WikipediaUrl]:
        urls = set()
        for template in self.templates:
            if template.urls:
                # aka merge the sets
                urls.update(template.urls)
        return urls

    @property
    def __find_bare_urls__(self) -> List[tuple]:
        """Return bare urls from the stripped wikitext"""
        return re.findall(
            r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?",
            self.get_stripped_wikicode,
        )

    @property
    def __bare_urls__(self) -> Set[WikipediaUrl]:
        """This returns a set"""
        urls = set()
        for url in self.__find_bare_urls__:
            # We get a tuple back so we join it
            urls.add(WikipediaUrl(url="".join(url)))
        return urls

    @property
    def urls(self) -> Set[WikipediaUrl]:
        """We support both URLs in templates and outside aka bare URLs
        This returns a union set"""
        urls: Set[WikipediaUrl] = set()
        urls.update(self.__template_urls__, self.__bare_urls__)
        return urls

    @property
    def check_urls(self):
        """This checks the status of all the URLs"""
        return [url.check() for url in self.urls]

    @property
    def first_level_domains(self) -> Set[str]:
        """This returns a set"""
        flds = set()
        for url in self.urls:
            url.get_first_level_domain()
            if url.first_level_domain:
                flds.add(url.first_level_domain)
        return flds

    @property
    def google_books_template_found(self):
        """Google books templates look like this:
        {{google books |plainurl=y |id=CDJpAAAAMAAJ |page=313}}"""
        for template in self.templates:
            if "google books" == template.name:
                return True
        return False

    @property
    def google_books_url_or_template_found(self):
        """This detects both google book template and google books url
        example: https://books.google.se/books?id=9HRodACJLOoC&printsec=
        frontcover&dq=test&hl=sv&sa=X&redir_esc=y#v=onepage&q=test&f=false"""
        return bool(
            bool("//books.google." in self.get_wikicode_as_string)
            or self.google_books_template_found
        )

    @property
    def web_archive_org_in_reference(self):
        return bool("web.archive.org" in self.get_wikicode_as_string)

    @property
    def archive_org_slash_details_in_reference(self):
        return bool("archive.org/details" in self.get_wikicode_as_string)

    @property
    def plain_text_in_reference(self) -> bool:
        # Try removing everything that is inside template markup and see if anything is left
        if isinstance(self.wikicode, Tag):
            stripped_wikicode = self.wikicode.contents.strip_code().strip()
        else:
            stripped_wikicode = self.wikicode.strip_code().strip()
        logger.debug(f"Stripped wikicode: '{stripped_wikicode}'")
        if len(stripped_wikicode) == 0:
            return False
        else:
            return True

    @property
    def cite_book_template_found(self) -> bool:
        return self.specific_template_found(names="cite book")

    @property
    def cite_journal_template_found(self) -> bool:
        return self.specific_template_found(names="cite journal")

    @property
    def cite_web_template_found(self) -> bool:
        return self.specific_template_found(names="cite web")

    @property
    def citation_template_found(self) -> bool:
        return self.specific_template_found(names=config.citation_template)

    @property
    def cs1_template_found(self) -> bool:
        for template in self.templates:
            if template.name in config.cs1_templates:
                return True
        return False

    @property
    def citeq_template_found(self) -> bool:
        for template in self.templates:
            if template.name in config.citeq_templates:
                return True
        return False

    @property
    def isbn_template_found(self) -> bool:
        return self.specific_template_found(names=config.isbn_template)

    @property
    def url_template_found(self) -> bool:
        return self.specific_template_found(names=config.url_template)

    @property
    def bare_url_template_found(self) -> bool:
        for template in self.templates:
            if config.bare_url_regex in template.name:
                return True
        return False

    @property
    def is_citation_reference(self):
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
    def first_template_name(self) -> str:
        """Helper method. We use this information in the graph to know which
        template the information in the reference came from"""
        if self.templates:
            return str(self.templates[0].name)
        else:
            return ""

    @property
    def number_of_templates(self) -> int:
        return len(self.templates)

    def __found_template__(self, name: str = "") -> bool:
        for template in self.templates:
            if name == template.name:
                return True
        return False

    def specific_template_found(self, names: Union[str, List[str]] = "") -> bool:
        """Used to search for a specific template"""
        if isinstance(names, list):
            for name in names:
                return self.__found_template__(name=name)
        else:
            return self.__found_template__(name=names)
        return False

    def __extract_templates_and_parameters_from_raw_reference__(self) -> None:
        """Helper method"""
        logger.debug("__extract_templates_and_parameters_from_raw_reference__: running")
        self.__extract_raw_templates__()
        self.__extract_and_clean_template_parameters__()

    def __extract_raw_templates__(self) -> None:
        """Extract the templates from self.wikicode"""
        logger.debug("__extract_raw_templates__: running")
        if not self.wikicode:
            raise MissingInformationError("self.wikicode was None")
        if isinstance(self.wikicode, str):
            raise MissingInformationError("self.wikicode was str")
        # Skip named references like "<ref name="INE"/>"
        wikicode_string = str(self.wikicode)
        if self.is_citation_reference and "</ref>" not in wikicode_string:
            logger.info(f"Skipping named reference with no content {wikicode_string}")
            self.is_named_reference = True
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
                self.templates.append(WikipediaTemplate(raw_template=raw_template))
            if count == 0:
                logger.debug(f"Found no templates in {self.wikicode}")

    def __extract_and_clean_template_parameters__(self) -> None:
        """We only extract and clean if exactly one template is found"""
        logger.debug("__extract_and_clean_template_parameters__: running")
        if self.number_of_templates == 1:
            [
                template.extract_and_prepare_parameter_and_flds()
                for template in self.templates
            ]

    def extract_and_determine_reference_type(self) -> None:
        """Helper method"""
        self.__extract_templates_and_parameters_from_raw_reference__()
        self.__determine_if_multiple_templates__()
        self.extraction_done = True

    def get_finished_wikipedia_reference_object(self) -> "WikipediaReference":
        """Make a WikipediaReference based on the extracted information"""
        logger.debug("get_finished_wikipedia_reference_object: running")
        if not self.extraction_done:
            self.extract_and_determine_reference_type()
        from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference

        if self.number_of_templates:
            reference = WikipediaReference(**self.templates[0].parameters)
        else:
            reference = WikipediaReference()
        # propagate attributes
        reference.raw_reference = self
        reference.cache = self.cache
        reference.wikibase = self.wikibase
        reference.finish_parsing_and_generate_hash(testing=self.testing)
        return reference

    def __determine_if_multiple_templates__(self):
        """We want to determine which type of reference this is

        Design limit: we only support one template for now"""
        if self.number_of_templates:
            logger.info(
                f"Found {self.number_of_templates} template(s) in {self.wikicode}"
            )
            if self.number_of_templates > 1:
                self.multiple_templates_found = True
                message = (
                    f"We found {self.number_of_templates} templates in "
                    f"{self.wikicode} -> templates: {self.templates} which is currently not supported"
                )
                logger.error(message)
                self.__log_to_file__(
                    message=message, file_name="multiple_template_error.log"
                )
