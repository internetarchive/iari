import logging
import re
from collections import OrderedDict
from typing import Any, List, Optional

from mwparserfromhell.nodes import Template  # type: ignore
from pydantic import validate_arguments

import config
from src.models.exceptions import MissingInformationError
from src.models.identifiers.doi import Doi
from src.models.wikimedia.wikipedia.url import WikipediaUrl
from src.wcd_base_model import WcdBaseModel

logger = logging.getLogger(__name__)


class WikipediaTemplate(WcdBaseModel):
    parameters: OrderedDict = OrderedDict()
    raw_template: Template
    extraction_done: bool = False
    doi_found: bool = False
    missing_or_empty_first_parameter: bool = False
    language_code: str = ""
    doi: Optional[Doi]

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    @property
    def doi_lookup_done(self) -> bool:
        if self.doi:
            return self.doi.doi_lookup_done
        else:
            return False

    @property
    def wikitext(self) -> str:
        return str(self.raw_template)

    @property
    def is_known_multiref_template(self) -> bool:
        return bool(self.name in config.known_multiref_templates)

    @property
    def is_isbn_template(self) -> bool:
        return bool(self.name in config.isbn_template)

    @property
    def is_bareurl_template(self) -> bool:
        return bool(self.name in config.citeq_templates)

    @property
    def is_citeq_template(self) -> bool:
        return bool(self.name in config.citeq_templates)

    @property
    def is_citation_template(self) -> bool:
        return bool(self.name in config.citation_template)

    @property
    def is_cs1_template(self) -> bool:
        return bool(self.name in config.cs1_templates)

    @property
    def is_url_template(self) -> bool:
        return bool(self.name in config.url_template)

    @property
    def is_webarchive_template(self) -> bool:
        return bool(self.name in config.webarchive_templates)

    @property
    def __first_parameter__(self) -> str:
        """Private helper method"""
        if not self.extraction_done:
            self.extract_and_prepare_parameter_and_flds()
        if self.parameters:
            if "first_parameter" in self.parameters.keys():
                return str(self.parameters["first_parameter"])
            else:
                return ""
        else:
            return ""

    @property
    def get_doi(self) -> str:
        """Helper method"""
        if not self.extraction_done:
            self.extract_and_prepare_parameter_and_flds()
        if "doi" in self.parameters.keys():
            return str(self.parameters["doi"])
        else:
            return ""

    def __extract_and_lookup_doi__(self) -> None:
        logger.debug("__extract_and_lookup_doi__: running")
        if self.parameters and "doi" in self.parameters:
            doi = self.parameters["doi"]
            if doi:
                self.doi_found = True
                self.doi = Doi(doi=doi)
                self.doi.lookup_doi()

    @property
    def get_isbn(self) -> str:
        """Helper method"""
        if self.name == "isbn":
            return self.__first_parameter__
        elif self.is_cs1_template:
            if "isbn" in self.parameters.keys():
                return str(self.parameters["isbn"])
        # Default to empty
        return ""

    # DISABLED because currently qid is unfortunately not a valid field on cs1 templates
    # @property
    # def get_qid(self) -> str:
    #     """Helper method"""
    #     if not self.parameters:
    #         raise MissingInformationError("no parameters")
    #     return self.parameters[""]

    @property
    def urls(self) -> List[WikipediaUrl]:
        """This returns a list"""
        # if not self.extracted:
        #     raise MissingInformationError("this template has not been extracted")
        urls = set()
        if "url" in self.parameters:
            url = self.parameters["url"]
            if url:
                logger.debug(f"url: {url}")
                urls.add(WikipediaUrl(url=url))
        if "archive_url" in self.parameters:
            url = self.parameters["archive_url"]
            if url:
                urls.add(WikipediaUrl(url=url))
        if "conference_url" in self.parameters:
            url = self.parameters["conference_url"]
            if url:
                urls.add(WikipediaUrl(url=url))
        if "transcript_url" in self.parameters:
            url = self.parameters["transcript_url"]
            if url:
                urls.add(WikipediaUrl(url=url))
        if "chapter_url" in self.parameters:
            url = self.parameters["chapter_url"]
            if url:
                urls.add(WikipediaUrl(url=url))
        return list(urls)

    @property
    def name(self):
        """Lowercased and stripped template name"""
        if not self.raw_template.name:
            raise MissingInformationError("self.raw_template.name was empty")
        return self.raw_template.name.strip().lower()

    def __add_template_name_to_parameters__(self):
        self.parameters["template_name"] = self.name

    @staticmethod
    def __remove_comments__(text: str):
        """Remove html comments <!-- -->
        Copyright pywikibot authors"""
        # This regex tries to match text on both sides of
        # the comment and join them or in the case no comment is found
        # just return the whole thing.
        regex = re.compile(r"(.*)<!--.*-->(.*)|(.*)")
        matches = re.findall(pattern=regex, string=text)
        if matches:
            # print(match.groups())
            string = ""
            for match in matches:
                # print(match)
                if match:
                    for part in match:
                        string += str(part)
            return string.strip()
        else:
            return text

    # noinspection PyShadowingNames
    @staticmethod
    def __explicit__(param):
        """Copyright pywikibot authors"""
        try:
            attr = param.showkey
        except AttributeError:
            attr = not param.positional
        return attr

    def __extract_and_clean_template_parameters__(self, strip: bool = True):
        """Return a list of references found in text.

        Return value is a list of tuples. There is one tuple for each use of a
        template in the page, with the template title as the first entry and a
        dict of parameters as the second entry. Parameters are indexed by
        strings; as in MediaWiki, an unnamed parameter is given a parameter name
        with an integer value corresponding to its position among the unnamed
        parameters, and if this results multiple parameters with the same name
        only the last value provided will be returned.

        This uses the package :py:obj:`mwparserfromhell` or
        :py:obj:`wikitextparser` as MediaWiki markup parser. It is mandatory
        that one of them is installed.

        There are minor differences between the two implementations.

        The parser packages preserves whitespace in parameter names and
        values.

        If there are multiple numbered parameters in the wikitext for the
        same position, MediaWiki will only use the last parameter value.
        e.g. `{{a| foo | 2 <!-- --> = bar | baz }}` is `{{a|1=foo|2=baz}}`
        To replicate that behaviour, enable both `remove_disabled_parts`
        and `strip` parameters.

        Copyright pywikibot authors
        """
        if not self.raw_template:
            raise MissingInformationError("self.raw_template was empty")

        # This has been disabled by Dennis
        # because it is not KISS and it relies on half of
        # pywikibot and we probably don't need it because
        # references are probably never inside disabled parts.
        # if remove_disabled_parts:
        #     text = removeDisabledParts(text)

        # Dennis removed the loop here during OOP-ification
        logger.debug(f"Working on template: {self.raw_template}")
        for parameter in self.raw_template.params:
            value = str(parameter.value)  # mwpfh needs upcast to str
            if strip:
                key = parameter.name.strip()
                if self.__explicit__(parameter):
                    value = parameter.value.strip()
                else:
                    value = str(parameter.value)
            else:
                key = str(parameter.name)
            # Remove comments added by Dennis
            # logger.debug(f"value before: {value}")
            cleaned_value = self.__remove_comments__(text=value)
            # logger.debug(f"value after: {value}")
            self.parameters[key] = cleaned_value

    def extract_and_prepare_parameter_and_flds(self) -> Any:
        logger.debug("extract_and_prepare_parameter_and_flds: running")
        self.__extract_and_clean_template_parameters__()
        self.__fix_key_names_in_template_parameters__()
        self.__add_template_name_to_parameters__()
        self.__rename_one_to_first_parameter__()
        self.__extract_and_lookup_doi__()
        self.extraction_done = True
        self.__detect_missing_first_parameter__()
        self.__extract_first_level_domains_from_urls__()

    def __fix_class_key__(self):
        """convert "class" key to "_class" to avoid collision with reserved python expression"""
        newdict = OrderedDict()
        for key in self.parameters:
            if key == "class":
                new_key = "news_class"
                newdict[new_key] = self.parameters[key]
            else:
                newdict[key] = self.parameters[key]
        self.parameters = newdict

    def __fix_aliases__(self):
        """Replace alias keys"""
        replacements = dict(
            accessdate="access_date",
            archiveurl="archive_url",
            archivedate="archive_date",
            ISBN="isbn",
            authorlink1="author_link1",
            authorlink2="author_link2",
            authorlink3="author_link3",
            authorlink4="author_link4",
            authorlink5="author_link5",
            authorurl="author_link",
        )
        newdict = OrderedDict()
        for key in self.parameters:
            replacement_made = False
            for replacement in replacements:
                if replacement == key:
                    new_key = replacements[key]
                    logger.debug(f"Replacing key {key} with {new_key}")
                    newdict[new_key] = self.parameters[key]
                    replacement_made = True
            if not replacement_made:
                newdict[key] = self.parameters[key]
        self.parameters = newdict

    def __fix_dash__(self):
        newdict = OrderedDict()
        for key in self.parameters:
            if "-" in key:
                new_key = key.replace("-", "_")
                newdict[new_key] = self.parameters[key]
            else:
                newdict[key] = self.parameters[key]
        self.parameters = newdict

    @validate_arguments
    def __fix_key_names_in_template_parameters__(self):
        """This avoids parse errors"""
        self.__fix_class_key__()
        self.__fix_aliases__()
        self.__fix_dash__()

    def __rename_one_to_first_parameter__(self):
        if "1" in self.parameters:
            logger.debug(f"Found first parameter '{self.parameters['1']}'")
            if not self.parameters["1"]:
                logger.debug(f"first parameter was empty")
            self.parameters["first_parameter"] = self.parameters["1"]
        else:
            logger.debug("No first parameter found")

    def __extract_first_level_domains_from_urls__(self):
        """Extract from all URLs"""
        [
            url.extract_first_level_domain()
            for url in self.urls
            if url.first_level_domain == ""
        ]

    def __detect_missing_first_parameter__(self):
        """Url, webarchive and isbn templates should always have a first parameter"""
        logger.debug("__detect_missing_first_parameter__: running")
        if (
            self.name in config.templates_with_mandatory_first_parameter
            and not self.__first_parameter__
        ):
            self.missing_or_empty_first_parameter = True

    @property
    def template_url(self) -> str:
        if not self.language_code:
            raise MissingInformationError("self.lang was empty")
        return f"https://en.wikipedia.org/wiki/Template:{self.name}"
