import logging
import re
from collections import OrderedDict
from typing import Any, Dict, List

from mwparserfromhell.nodes import Template  # type: ignore
from pydantic import BaseModel, validate_arguments

from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.url import WikipediaUrl

logger = logging.getLogger(__name__)


class WikipediaTemplate(BaseModel):
    parameters: OrderedDict = OrderedDict()
    # We allow union here to enable easier testing
    raw_template: Template  # Union[Template, str]
    extraction_done: bool = False
    missing_or_empty_first_parameter: bool = False
    # language_code: str = ""  # Used only to generate the URI for the template
    isbn: str = ""

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    @property
    def wikitext(self) -> str:
        return str(self.raw_template)

    @property
    def __first_parameter__(self) -> str:
        """Private helper method"""
        if self.parameters:
            if "first_parameter" in self.parameters.keys():
                return str(self.parameters["first_parameter"])
            else:
                return ""
        else:
            return ""

    def __extract_isbn__(self) -> None:
        """Extract ISBN to make the life of data consumers a little bit easier"""
        # todo make this work for multiple language editions
        if self.name == "isbn":
            self.isbn = self.__first_parameter__
        else:
            if "isbn" in self.parameters.keys():
                self.isbn = str(self.parameters["isbn"])

    @property
    def urls(self) -> List[WikipediaUrl]:
        """This returns a list"""
        # if not self.extracted:
        #     raise MissingInformationError("this templates has not been extracted")
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
        """Lowercased and stripped templates name"""
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
        templates in the page, with the templates title as the first entry and a
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
        from src import app

        if not self.raw_template:
            raise MissingInformationError("self.raw_template was empty")

        # This has been deprecated by Dennis
        # because it is not KISS and it relies on half of
        # pywikibot and we probably don't need it because
        # references are probably never inside deprecated parts.
        # if remove_disabled_parts:
        #     text = removeDisabledParts(text)

        # Dennis removed the loop here during OOP-ification
        app.logger.debug(f"Working on templates: {self.raw_template}")
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
        from src import app

        app.logger.debug("extract_and_prepare_parameter_and_flds: running")
        self.__extract_and_clean_template_parameters__()
        self.__fix_key_names_in_template_parameters__()
        self.__add_template_name_to_parameters__()
        self.__rename_one_to_first_parameter__()
        self.__extract_isbn__()
        self.extraction_done = True
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
                logger.debug("first parameter was empty")
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

    def get_dict(self) -> Dict[str, Any]:
        """Return a dict that we can output to patrons via the API"""
        return dict(parameters=self.parameters, isbn=self.isbn)
