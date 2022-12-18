import logging
import re
from collections import OrderedDict

from mwparserfromhell.nodes import Template  # type: ignore
from pydantic import validate_arguments

from src.models.exceptions import MissingInformationError
from src.wcd_base_model import WcdBaseModel

logger = logging.getLogger(__name__)

class WikipediaTemplate(WcdBaseModel):
    parameters: OrderedDict = OrderedDict()
    raw_template: Template

    class Config:
        arbitrary_types_allowed = True


    @property
    def name(self):
        """Lowercased template name"""
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

    def __extract_and_clean_template_parameters__(self, strip: bool = False):
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
        for parameter in getattr(self.raw_template, "params"):
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

    def extract_and_prepare_parameters(self):
        self.__extract_and_clean_template_parameters__()
        self.__fix_key_names_in_template_parameters__()
        self.__add_template_name_to_parameters__()

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
            authorlink="author_link",
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
