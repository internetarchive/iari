import logging
import re
from typing import List, Optional

from pydantic import validate_arguments

from src import WcdBaseModel
from src.models.exceptions import LanguageNotSupportedError, MoreThanOneNumberError
from src.models.wikimedia.wikipedia.reference.enums import (
    EnglishWikipediaTemplatePersonRole,
)
from src.models.wikimedia.wikipedia.reference.template.person import Person
from src.models.wikimedia.wikipedia.reference.template.template import WikipediaTemplate

logger = logging.getLogger(__name__)

# todo copy code from v2.0.0. that populate:
# first_lasts: List = []
# numbered_first_lasts: List = []

# todo add tests


class Persons(WcdBaseModel):
    """This class handles all parsing of persons"""

    lang: str = "en"
    template: WikipediaTemplate
    first_lasts: List = []
    numbered_first_lasts: List = []

    @property
    def attributes(self):
        return self.template.parameters

    def parse(self):
        if not self.lang == "en":
            raise LanguageNotSupportedError()
        # load parser for this language version

    def __parse_persons__(self) -> None:
        """Parse all person related data into Person objects"""
        # find all the attributes but exclude the properties as they lead to weird errors
        self.authors_list = self.__parse_known_role_persons__(
            role=EnglishWikipediaTemplatePersonRole.AUTHOR
        )
        self.editors_list = self.__parse_known_role_persons__(
            role=EnglishWikipediaTemplatePersonRole.EDITOR
        )
        self.hosts_list = self.__parse_known_role_persons__(
            role=EnglishWikipediaTemplatePersonRole.HOST
        )
        self.interviewers_list = self.__parse_known_role_persons__(
            role=EnglishWikipediaTemplatePersonRole.INTERVIEWER
        )
        self.persons_without_role = self.__parse_roleless_persons__()
        self.translators_list = self.__parse_known_role_persons__(
            role=EnglishWikipediaTemplatePersonRole.TRANSLATOR
        )

    @validate_arguments
    def __parse_roleless_persons__(self) -> List[Person]:
        from src.models.api import app

        persons = []
        # first last
        unnumbered_first_last = [
            attribute
            for attribute in self.attributes
            if self.__find_number__(attribute) is None
            and (attribute == "first" or attribute == "last")
        ]
        app.logger.debug(f"{len(unnumbered_first_last)} unnumbered first lasts found.")
        if len(unnumbered_first_last) > 0:
            person = Person(
                role=EnglishWikipediaTemplatePersonRole.UNKNOWN,
            )
            for attribute in unnumbered_first_last:
                # print(attribute, getattr(self, attribute))
                if attribute == "first":
                    person.given = attribute["first"]
                if attribute == "last":
                    person.surname = attribute["last"]
            # console.print(person)
            persons.append(person)
            # exit()
        # We use list comprehension to get the numbered persons to
        # ease code maintentenance and easily support a larger range if necessary
        persons.extend(self.__get_numbered_persons__())
        return persons

    @validate_arguments
    def __parse_known_role_persons__(
        self, role: EnglishWikipediaTemplatePersonRole
    ) -> List[Person]:
        persons = []
        person_without_number = [
            attribute
            for attribute in self.attributes
            if self.__find_number__(attribute) is None and str(role.value) in attribute
        ]
        if len(person_without_number) > 0:
            person = Person(role=role)
            link = role.value + "_link"
            mask = role.value + "_mask"
            first = role.value + "_first"
            last = role.value + "_last"
            for attribute in person_without_number:
                # print(attribute, getattr(self, attribute))
                if attribute == role.value:
                    person.name_string = getattr(self, str(role.value))
                if attribute == link:
                    person.link = getattr(self, link)
                if attribute == mask:
                    person.mask = getattr(self, mask)
                if attribute == first:
                    person.given = getattr(self, first)
                if attribute == last:
                    person.surname = getattr(self, last)
            persons.append(person)
        # We use list comprehension to get the numbered persons to
        # ease code maintentenance and easily support a larger range if necessary
        persons.extend(
            self.__get_numbered_persons__(
                role=EnglishWikipediaTemplatePersonRole.AUTHOR,
                search_string=str(role.value),
            )
        )
        # console.print(f"{role.name}s: {persons}")
        return persons

    @validate_arguments
    def __get_numbered_persons__(
        self,
        role: EnglishWikipediaTemplatePersonRole = None,
        search_string: str = None,
    ) -> List[Person]:
        """This is just a helper function to call __get_numbered_person__"""
        # Mypy warns that the following could add None to the list,
        # but that cannot happen.
        maybe_persons = [
            self.__get_numbered_person__(
                number=number,
                role=role,
                search_string=search_string,
            )
            for number in range(1, 14)
        ]
        # We discard all None-values here to placate mypy
        return [i for i in maybe_persons if i]

    @validate_arguments
    def __get_numbered_person__(
        self,
        number: int,
        role: EnglishWikipediaTemplatePersonRole = None,
        search_string: str = None,
    ) -> Optional[Person]:
        """This functions gets all types of numbered persons,
        both those with roles and those without"""
        # First handle persons with a role
        if role is not None and search_string is not None:
            # Collect all attributes
            matching_attributes = [
                attribute
                for attribute in self.attributes
                if search_string in attribute and getattr(self, attribute) is not None
            ]
            # Find the attributes with the correct number
            found_attributes = [
                attribute
                for attribute in matching_attributes
                if self.__find_number__(attribute) == number
            ]
            if len(found_attributes) > 0:
                person = Person(role=role, number_in_sequence=number)
                for attribute in found_attributes:
                    # logger.debug(attribute, getattr(self, attribute))
                    # Handle attributes with a number in the end. E.g. "author_link1"
                    if attribute == search_string + str(number):
                        person.name_string = getattr(self, search_string + str(number))
                    if attribute == search_string + "_link" + str(number):
                        person.link = getattr(
                            self, search_string + "_link" + str(number)
                        )
                    if attribute == search_string + "_mask" + str(number):
                        person.mask = getattr(
                            self, search_string + "_mask" + str(number)
                        )
                    if attribute == search_string + "_first" + str(number):
                        person.given = getattr(
                            self, search_string + "_first" + str(number)
                        )
                    if attribute == search_string + "_last" + str(number):
                        person.surname = getattr(
                            self, search_string + "_last" + str(number)
                        )
                    # str(number) after author. E.g. "author1_link"
                    if attribute == search_string + str(number) + "_link":
                        person.link = getattr(
                            self, search_string + str(number) + "_link"
                        )
                    if attribute == search_string + str(number) + "_mask":
                        person.mask = getattr(
                            self, search_string + str(number) + "_mask"
                        )
                    if attribute == search_string + str(number) + "_first":
                        person.given = getattr(
                            self, search_string + str(number) + "_first"
                        )
                    if attribute == search_string + str(number) + "_last":
                        person.surname = getattr(
                            self, search_string + str(number) + "_last"
                        )
                # Guard against empty person objects being returned
                if (
                    person.given and person.surname
                ) is not None or person.name_string is not None:
                    person.number_in_sequence = number
                    return person
                else:
                    logger.debug(
                        f"Discarded {person} because it did not have both given- and surnames or name_string"
                    )
                    return None
            else:
                return None
        else:
            # Support cite journal first[1-12] and last[1-12]
            if self.first_lasts is None:
                self.first_lasts = [
                    attribute
                    for attribute in self.attributes
                    if ("first" in attribute or "last" in attribute)
                    and getattr(self, attribute) is not None
                ]
            logger.debug(f"{len(self.first_lasts)} first lasts found.")
            if self.numbered_first_lasts is None:
                self.numbered_first_lasts = [
                    attribute
                    for attribute in self.first_lasts
                    if self.__find_number__(attribute) == number
                ]
            logger.debug(
                f"{len(self.numbered_first_lasts)} numbered first lasts found with number {number}."
            )
            if len(self.numbered_first_lasts) > 0:
                person = Person(
                    role=EnglishWikipediaTemplatePersonRole.UNKNOWN,
                )
                for attribute in self.numbered_first_lasts:
                    # logger.debug(attribute, getattr(self, attribute))
                    first = "first" + str(number)
                    last = "last" + str(number)
                    if attribute == first:
                        person.given = getattr(self, first)
                    if attribute == last:
                        person.surname = getattr(self, last)
                # Guard against empty person objects being returned
                if (
                    person.given and person.surname
                ) is not None or person.name_string is not None:
                    person.number_in_sequence = number
                    return person
                else:
                    logger.debug(
                        f"Discarded {person} because it did not have both given- and surnames or name_string"
                    )
                    return None
            else:
                return None

    @staticmethod
    @validate_arguments
    def __find_number__(string: str) -> Optional[int]:
        """Find all numbers in a string"""
        # logger.debug(f"Trying to find numbers in: {string}.")
        numbers = re.findall(r"\d+", string)
        if len(numbers) == 1:
            return int(numbers[0])
        elif len(numbers) > 1:
            raise MoreThanOneNumberError(f"found {numbers}")
        else:
            logger.debug(f"Found no numbers.")
            return None
