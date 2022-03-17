import logging
from datetime import datetime
from typing import Optional, List

from marshmallow import (
    Schema,
)
from marshmallow.fields import String
from pydantic import BaseModel, validator, validate_arguments

from src import console
from src.models.enums import Role
from src.models.exceptions import MoreThanOneNumberError
from src.models.person import Person

logger = logging.getLogger(__name__)

# We use marshmallow here because pydantic did not seem to support optional alias fields.
# https://github.com/samuelcolvin/pydantic/discussions/3855


class WikipediaPageReference(BaseModel):
    """This models any reference on a Wikipedia page

    Do we want to merge page + pages into a string property like in Wikidata?
    How do we handle parse errors? In a file log? Should we publish the log for Wikipedians to fix?

    Validation works better with pydantic so we validate when creating this object

    Support date ranges like "May-June 2011"? See https://stackoverflow.com/questions/10340029/
    """

    authors: Optional[List[Person]]
    editors: Optional[List[Person]]
    hosts: Optional[List[Person]]
    interviewers: Optional[List[Person]]
    template_name: str  # We use this to keep track of which template the information came from
    translators: Optional[List[Person]]
    persons_without_role: Optional[List[Person]]

    # These are all the parameters in the supported templates
    #######################
    # Names
    #######################
    # FIXME of what?
    first1: Optional[str]
    first2: Optional[str]
    first3: Optional[str]
    first4: Optional[str]
    first5: Optional[str]
    first6: Optional[str]
    first: Optional[str]
    last1: Optional[str]
    last2: Optional[str]
    last3: Optional[str]
    last4: Optional[str]
    last5: Optional[str]
    last6: Optional[str]
    last: Optional[str]

    #######################
    # Author first/given (equal)
    #######################
    author_given: Optional[str]
    author_given1: Optional[str]
    author_given2: Optional[str]
    author_given3: Optional[str]
    author_given4: Optional[str]
    author_given5: Optional[str]
    author_first: Optional[str]
    author_first1: Optional[str]
    author_first2: Optional[str]
    author_first3: Optional[str]
    author_first4: Optional[str]
    author_first5: Optional[str]

    #######################
    # Author last/surname (equal)
    #######################
    author_surname: Optional[str]
    author_surname1: Optional[str]
    author_surname2: Optional[str]
    author_surname3: Optional[str]
    author_surname4: Optional[str]
    author_surname5: Optional[str]
    author_last: Optional[str]
    author_last1: Optional[str]
    author_last2: Optional[str]
    author_last3: Optional[str]
    author_last4: Optional[str]
    author_last5: Optional[str]

    # Author
    author: Optional[str]
    author_link1: Optional[str]
    author_link2: Optional[str]
    author_link3: Optional[str]
    author_link4: Optional[str]
    author_link5: Optional[str]
    author_link: Optional[str]
    author_mask1: Optional[str]
    author_mask2: Optional[str]
    author_mask3: Optional[str]
    author_mask4: Optional[str]
    author_mask5: Optional[str]
    author_mask: Optional[str]

    #######################
    # Editor
    #######################
    editor1_first: Optional[str]
    editor1_last: Optional[str]
    editor1_link: Optional[str]
    editor2_first: Optional[str]
    editor2_last: Optional[str]
    editor2_link: Optional[str]
    editor3_first: Optional[str]
    editor3_last: Optional[str]
    editor3_link: Optional[str]
    editor4_first: Optional[str]
    editor4_last: Optional[str]
    editor4_link: Optional[str]
    editor5_first: Optional[str]
    editor5_last: Optional[str]
    editor5_link: Optional[str]
    editor: Optional[str]
    editor_first1: Optional[str]
    editor_first2: Optional[str]
    editor_first3: Optional[str]
    editor_first4: Optional[str]
    editor_first5: Optional[str]
    editor_first: Optional[str]
    editor_last1: Optional[str]
    editor_last2: Optional[str]
    editor_last3: Optional[str]
    editor_last4: Optional[str]
    editor_last5: Optional[str]
    editor_last: Optional[str]
    editor_link1: Optional[str]
    editor_link2: Optional[str]
    editor_link3: Optional[str]
    editor_link4: Optional[str]
    editor_link5: Optional[str]
    editor_link: Optional[str]
    editor_mask1: Optional[str]
    editor_mask2: Optional[str]
    editor_mask3: Optional[str]
    editor_mask4: Optional[str]
    editor_mask5: Optional[str]
    editor_mask: Optional[str]

    #######################
    # Translator
    #######################
    translator_first1: Optional[str]
    translator_first2: Optional[str]
    translator_first3: Optional[str]
    translator_first4: Optional[str]
    translator_first5: Optional[str]
    translator_first: Optional[str]
    translator_last1: Optional[str]
    translator_last2: Optional[str]
    translator_last3: Optional[str]
    translator_last4: Optional[str]
    translator_last5: Optional[str]
    translator_last: Optional[str]
    translator_link1: Optional[str]
    translator_link2: Optional[str]
    translator_link3: Optional[str]
    translator_link4: Optional[str]
    translator_link5: Optional[str]
    translator_link: Optional[str]
    translator_mask1: Optional[str]
    translator_mask2: Optional[str]
    translator_mask3: Optional[str]
    translator_mask4: Optional[str]
    translator_mask5: Optional[str]
    translator_mask: Optional[str]

    #######################
    # Interviewer
    #######################
    interviewer_given: Optional[str]
    interviewer_first: Optional[str]
    interviewer_surname: Optional[str]
    interviewer_last: Optional[str]

    #######################
    # Host
    #######################
    host: Optional[str]
    host1: Optional[str]
    host2: Optional[str]
    host3: Optional[str]
    host4: Optional[str]
    host5: Optional[str]

    #######################
    # Boolean switches
    #######################
    display_authors: Optional[str]  # we can ignore this one
    display_editors: Optional[str]  # we can ignore this one
    display_translators: Optional[str]  # we can ignore this one
    display_subjects: Optional[str]  # we can ignore this one

    # Others
    access_date: Optional[datetime]
    agency: Optional[str]  # what is this?
    archive_date: Optional[datetime]
    archive_url: Optional[str]
    arxiv: Optional[str]
    asin: Optional[str]  # what is this?
    asin_tld: Optional[str]
    at: Optional[str]  # what is this?
    bibcode: Optional[str]
    bibcode_access: Optional[str]
    biorxiv: Optional[str]
    book_title: Optional[str]
    chapter: Optional[str]
    chapter_format: Optional[str]
    chapter_url: Optional[str]
    chapter_url_access: Optional[str]
    citeseerx: Optional[str]
    news_class: Optional[str]  # used in cite arxiv
    conference: Optional[str]
    conference_url: Optional[str]
    date: Optional[datetime]
    degree: Optional[str]
    department: Optional[str]
    doi: Optional[str]
    doi_access: Optional[str]
    doi_broken_date: Optional[datetime]
    edition: Optional[str]
    eissn: Optional[str]
    encyclopedia: Optional[str]
    eprint: Optional[str]
    format: Optional[str]
    hdl: Optional[str]
    hdl_access: Optional[str]
    id: Optional[str]  # where does this come from?
    isbn: Optional[str]
    ismn: Optional[str]
    issn: Optional[str]
    issue: Optional[str]
    jfm: Optional[str]
    journal: Optional[str]
    jstor: Optional[str]
    jstor_access: Optional[str]
    language: Optional[str]  # do we want to parse this?
    lccn: Optional[str]
    location: Optional[str]
    mode: Optional[str]  # what is this?
    mr: Optional[str]
    name_list_style: Optional[str]
    no_pp: Optional[str]
    oclc: Optional[str]
    ol: Optional[str]  # what is this?
    ol_access: Optional[str]
    orig_date: Optional[datetime]
    orig_year: Optional[datetime]
    osti: Optional[str]  # what is this?
    osti_access: Optional[str]
    others: Optional[str]  # what is this?
    page: Optional[str]
    pages: Optional[str]
    pmc: Optional[str]
    pmc_embargo_date: Optional[datetime]
    pmid: Optional[str]
    postscript: Optional[str]  # what is this?
    publication_date: Optional[datetime]
    publication_place: Optional[str]
    publisher: Optional[str]
    quote: Optional[str]  # do we want to store this?
    quote_page: Optional[str]
    quote_pages: Optional[str]
    ref: Optional[str]
    registration: Optional[str]  # what is this?
    rfc: Optional[str]  # what is this?
    s2cid: Optional[str]
    s2cid_access: Optional[str]
    sbn: Optional[str]
    script_chapter: Optional[str]
    script_quote: Optional[str]
    script_title: Optional[str]
    series: Optional[str]
    ssrn: Optional[str]
    subject: Optional[str]
    subject_mask: Optional[str]
    subscription: Optional[str]
    title: Optional[str]
    title_link: Optional[str]
    trans_chapter: Optional[str]  # this is a translation of a chapter
    trans_quote: Optional[str]  # this is a translation of a quote
    trans_title: Optional[str]  # this is a translation of a title
    type: Optional[str]  # what is this?
    url: Optional[str]
    url_access: Optional[str]
    url_status: Optional[str]
    via: Optional[str]  # what is this?
    volume: Optional[str]
    website: Optional[str]
    work: Optional[str]
    year: Optional[str]
    zbl: Optional[str]  # what is this?

    #######################
    # Deprecated parameters
    #######################
    # We ignore these
    # cite news
    lay_date: Optional[str]
    lay_format: Optional[str]
    lay_source: Optional[str]
    lay_url: Optional[str]
    transcripturl: Optional[str]

    # Numbered parameters
    first_parameter: Optional[str]  # 1
    second_parameter: Optional[str]  # 2

    # Fields found in the wild
    df: Optional[str]
    magazine: Optional[str]
    newspaper: Optional[str]
    author1: Optional[str]
    author2: Optional[str]
    author3: Optional[str]
    author4: Optional[str]
    author5: Optional[str]
    author6: Optional[str]
    author7: Optional[str]
    author8: Optional[str]
    author9: Optional[str]
    author10: Optional[str]
    editor1: Optional[str]
    editor2: Optional[str]
    editor3: Optional[str]
    editor4: Optional[str]
    editor5: Optional[str]
    number: Optional[str]
    first7: Optional[str]
    first8: Optional[str]
    first9: Optional[str]
    first10: Optional[str]
    last7: Optional[str]
    last8: Optional[str]
    last9: Optional[str]
    last10: Optional[str]
    message_id: Optional[str]
    newsgroup: Optional[str]
    archive_format: Optional[str]
    time: Optional[datetime]
    interviewer: Optional[str]
    medium: Optional[str]

    @staticmethod
    def __find_number__(string: str):
        numbers = []
        for char in string.split():
            if char.isdigit():
                numbers.append(int(char))
        if len(numbers) > 0:
            return numbers[0]
        elif len(numbers) > 1:
            raise MoreThanOneNumberError()
        else:
            return None

    def __parse_editors__(self, attributes: List[str]):
        editors = []
        # editor with no given or surname
        editor = [
            attribute
            for attribute in attributes
            if self.__find_number__(attribute) is None
            and (
                attribute == "editor"
                or attribute == "editor_link"
                or attribute == "editor_mask"
            )
        ]
        if len(editor) > 0:
            person = Person(role=Role.EDITOR, has_number=False)
            for attribute in editor:
                # print(attribute, getattr(self, attribute))
                if attribute == "editor":
                    person.name_string = self.editor
                if attribute == "editor_link":
                    person.link = self.editor_link
                if attribute == "editor_mask":
                    person.mask = self.editor_mask
            # console.print(person)
            editors.append(person)
            # exit()
        # editor with no given or surname
        editor = [
            attribute
            for attribute in attributes
            if self.__find_number__(attribute) is None
            and (
                attribute == "editor"
                or attribute == "editor_link"
                or attribute == "editor_mask"
            )
        ]
        if len(editor) > 0:
            person = Person(role=Role.EDITOR, has_number=False)
            for attribute in editor:
                # print(attribute, getattr(self, attribute))
                if attribute == "editor":
                    person.name_string = self.editor
                if attribute == "editor_link":
                    person.link = self.editor_link
                if attribute == "editor_mask":
                    person.mask = self.editor_mask
            # console.print(person)
            editors.append(person)
            # exit()
        # We use list comprehension to get the numbered persons to
        # ease code maintentenance and easily support a larger range if neccessary
        editors.extend(
            self.__get_numbered_persons__(
                attributes=attributes, role=Role.EDITOR, search_string="editor"
            )
        )
        console.print(f"editors: {editors}")
        if len(editors) > 1:
            exit()
        return editors

    @validate_arguments
    def __get_numbered_persons__(
        self, attributes: List[str], role: Role, search_string: str
    ):
        return [
            self.__get_numbered_person__(
                attributes=attributes,
                number=number,
                role=Role.EDITOR,
                search_string=search_string,
            )
            for number in range(1, 12)
            if self.__get_numbered_person__(
                attributes=attributes,
                number=number,
                role=Role.EDITOR,
                search_string=search_string,
            )
            is not None
        ]

    @validate_arguments
    def __get_numbered_person__(
        self, attributes: List[str], number: int, role: Role, search_string: str
    ):
        author = [
            attributes
            for attribute in attributes
            if self.__find_number__(attribute) == number and search_string in attribute
        ]
        if len(author) > 0:
            person = Person(role=role, has_number=True, number_in_sequence=number)
            for attribute in author:
                print(attribute, getattr(self, attribute))
                if attribute == search_string + "1":
                    person.name_string = getattr(self, search_string + number)
                if attribute == search_string + "_link1":
                    person.link = getattr(self, search_string + "_link" + number)
                if attribute == search_string + "_mask1":
                    person.mask = getattr(self, search_string + "_mask" + number)
                if attribute == search_string + "_first1":
                    person.given = getattr(self, search_string + "_first" + number)
                if attribute == search_string + "_last1":
                    person.surname = getattr(self, search_string + "_last" + number)
            return person

    def __parse_authors__(self, attributes: List[str]):
        authors = []
        author_without_number = [
            attribute
            for attribute in attributes
            if self.__find_number__(attribute) is None and "author" in attribute
        ]
        if len(author_without_number) > 0:
            person = Person(role=Role.AUTHOR, has_number=False)
            for attribute in author_without_number:
                print(attribute, getattr(self, attribute))
                if attribute == "author":
                    person.name_string = self.author
                if attribute == "author_link":
                    person.link = self.author_link
                if attribute == "author_mask":
                    person.mask = self.author_mask
                if attribute == "author_first":
                    person.given = self.author_first
                if attribute == "author_last":
                    person.surname = self.author_last
            authors.append(person)
        # We use list comprehension to get the numbered persons to
        # ease code maintentenance and easily support a larger range if neccessary
        authors.extend(
            self.__get_numbered_persons__(
                attributes=attributes, role=Role.AUTHOR, search_string="author"
            )
        )
        console.print(f"authors: {authors}")
        if len(authors) > 1:
            exit()
        return authors

    def __parse_roleless_persons__(self, attributes: List[str]):
        persons = []
        # first last
        unnumbered_first_last = [
            attribute
            for attribute in attributes
            if self.__find_number__(attribute) is None
            and (attribute == "first" or attribute == "last")
        ]
        if len(unnumbered_first_last) > 0:
            person = Person(role=Role.UNKNOWN, has_number=False)
            for attribute in unnumbered_first_last:
                # print(attribute, getattr(self, attribute))
                if attribute == "first":
                    person.given = self.first
                if attribute == "last":
                    person.surname = self.last
            # console.print(person)
            persons.append(person)
            # exit()
        # TODO add support for numbered parameters first1, etc.
        return persons

    def parse_persons(self):
        """Parse all person related data into Person objects"""
        # find all the attributes
        attributes = [
            a
            for a in dir(self)
            if not a.startswith("_")
            and not callable(getattr(self, a))
            and getattr(self, a) is not None
        ]
        self.authors = self.__parse_authors__(attributes=attributes)
        self.editors = self.__parse_editors__(attributes=attributes)
        self.persons_without_role = self.__parse_roleless_persons__(
            attributes=attributes
        )
        # translators = self.__parse_authors__(attributes=attributes)
        # numbered_attributes_to_check = []
        # for attribute in attributes:
        #     person = Person()
        #     print(attribute, getattr(self, attribute))
        #
        #     if attribute.startswith("first"):
        #         logger.debug("found first")
        #         # detect number
        #         number = find_number(attribute)
        #         if number:
        #             person.number_in_sequence = number
        #         # parsing up to 12 numbered persons
        #         for number in range(1, 12):
        #             logger.debug("found first")
        #     if attribute.startswith("last"):
        #         logger.debug("found last")
        #     if attribute.startswith("editor"):
        #         logger.debug("found editor")
        #     if attribute.startswith("translator"):
        #         logger.debug("found editor")
        #
        # exit()

    @validator(
        "access_date",
        "archive_date",
        "date",
        "doi_broken_date",
        "orig_date",
        "orig_year",
        "pmc_embargo_date",
        "publication_date",
        "time",
        pre=True,
    )
    def __validate_time__(cls, v):
        """Pydantic validator
        see https://stackoverflow.com/questions/66472255/"""
        date = None
        # Support "2013-01-01"
        try:
            date = datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            pass
        # Support "May 9, 2013"
        try:
            date = datetime.strptime(v, "%B %d, %Y")
        except ValueError:
            pass
        # Support "Jul 9, 2013"
        try:
            date = datetime.strptime(v, "%b %d, %Y")
        except ValueError:
            pass
        # Support "May 25, 2012a"
        try:
            date = datetime.strptime(v[:-1], "%b %d, %Y")
        except ValueError:
            pass
        # Support "1 September 2003"
        try:
            date = datetime.strptime(v, "%d %B %Y")
        except ValueError:
            pass
        # Support "26 Dec 1996"
        try:
            date = datetime.strptime(v, "%d %b %Y")
        except ValueError:
            pass
        # Support "September 2003"
        try:
            date = datetime.strptime(v, "%B %Y")
        except ValueError:
            pass
        # Support "Sep 2003"
        try:
            date = datetime.strptime(v, "%b %Y")
        except ValueError:
            pass
        # Support "2003"
        try:
            date = datetime.strptime(v, "%Y")
        except ValueError:
            pass
        if date is None:
            # raise TimeParseException(f"date format '{v}' not supported yet")
            logger.warning(f"date format '{v}' not supported yet")
        return date


class WikipediaPageReferenceSchema(Schema):
    """Marshmellow schema to load the attributes using aliases

    We don't validate with marshmellow because it does not seem to work correctly."""

    first_parameter = String(data_key="1")
    second_parameter = String(data_key="2")
    template_name = String(required=True)

    class Meta:
        additional = (
            # found in the wild
            "df",
            "magazine",
            "newspaper",
            "author1",
            "author2",
            "author3",
            "author4",
            "author5",
            "author6",
            "author7",
            "author8",
            "author9",
            "author10",
            "editor1",
            "editor2",
            "editor3",
            "editor4",
            "editor5",
            "number",
            "first7",
            "first8",
            "first9",
            "first10",
            "first11",
            "first12",
            "last7",
            "last8",
            "last9",
            "last10",
            "last11",
            "last12",
            "message_id",
            "newsgroup",
            "archive_format",
            "time",
            "interviewer",
            "medium",
            # dates,
            "access_date",
            "archive_date",
            "date",
            "doi_broken_date",
            "orig_date",
            "orig_year",
            "pmc_embargo_date",
            "publication_date",
            # from template documentation
            "first1",
            "first2",
            "first3",
            "first4",
            "first5",
            "first6",
            "first",
            "last1",
            "last2",
            "last3",
            "last4",
            "last5",
            "last6",
            "last",
            "author_given",
            "author_given1",
            "author_given2",
            "author_given3",
            "author_given4",
            "author_given5",
            "author_first",
            "author_first1",
            "author_first2",
            "author_first3",
            "author_first4",
            "author_first5",
            "author_surname",
            "author_surname1",
            "author_surname2",
            "author_surname3",
            "author_surname4",
            "author_surname5",
            "author_last",
            "author_last1",
            "author_last2",
            "author_last3",
            "author_last4",
            "author_last5",
            "author",
            "author_link1",
            "author_link2",
            "author_link3",
            "author_link4",
            "author_link5",
            "author_link",
            "author_mask1",
            "author_mask2",
            "author_mask3",
            "author_mask4",
            "author_mask5",
            "author_mask",
            "editor1_first",
            "editor1_last",
            "editor1_link",
            "editor2_first",
            "editor2_last",
            "editor2_link",
            "editor3_first",
            "editor3_last",
            "editor3_link",
            "editor4_first",
            "editor4_last",
            "editor4_link",
            "editor5_first",
            "editor5_last",
            "editor5_link",
            "editor",
            "editor_first1",
            "editor_first2",
            "editor_first3",
            "editor_first4",
            "editor_first5",
            "editor_first",
            "editor_last1",
            "editor_last2",
            "editor_last3",
            "editor_last4",
            "editor_last5",
            "editor_last",
            "editor_link1",
            "editor_link2",
            "editor_link3",
            "editor_link4",
            "editor_link5",
            "editor_link",
            "editor_mask1",
            "editor_mask2",
            "editor_mask3",
            "editor_mask4",
            "editor_mask5",
            "editor_mask",
            "translator_first1",
            "translator_first2",
            "translator_first3",
            "translator_first4",
            "translator_first5",
            "translator_first",
            "translator_last1",
            "translator_last2",
            "translator_last3",
            "translator_last4",
            "translator_last5",
            "translator_last",
            "translator_link1",
            "translator_link2",
            "translator_link3",
            "translator_link4",
            "translator_link5",
            "translator_link",
            "translator_mask1",
            "translator_mask2",
            "translator_mask3",
            "translator_mask4",
            "translator_mask5",
            "translator_mask",
            "interviewer_given",
            "interviewer_first",
            "interviewer_surname",
            "interviewer_last",
            "host",
            "host1",
            "host2",
            "host3",
            "host4",
            "host5",
            "display_authors",
            "display_editors",
            "display_translators",
            "display_subjects",
            "agency",
            "archive_url",
            "arxiv",
            "asin",
            "asin_tld",
            "at",
            "bibcode",
            "bibcode_access",
            "biorxiv",
            "book_title",
            "chapter",
            "chapter_format",
            "chapter_url",
            "chapter_url_access",
            "citeseerx",
            "news_class",
            "conference",
            "conference_url",
            "degree",
            "department",
            "doi",
            "doi_access",
            "edition",
            "eissn",
            "encyclopedia",
            "eprint",
            "format",
            "hdl",
            "hdl_access",
            "id",
            "isbn",
            "ismn",
            "issn",
            "issue",
            "jfm",
            "journal",
            "jstor",
            "jstor_access",
            "language",
            "lccn",
            "location",
            "mode",
            "mr",
            "name_list_style",
            "no_pp",
            "oclc",
            "ol",
            "ol_access",
            "osti",
            "osti_access",
            "others",
            "page",
            "pages",
            "pmc",
            "",
            "pmid",
            "postscript",
            "",
            "publication_place",
            "publisher",
            "quote",
            "quote_page",
            "quote_pages",
            "ref",
            "registration",
            "rfc",
            "s2cid",
            "s2cid_access",
            "sbn",
            "script_chapter",
            "script_quote",
            "script_title",
            "series",
            "ssrn",
            "subject",
            "subject_mask",
            "subscription",
            "title",
            "title_link",
            "trans_chapter",
            "trans_quote",
            "trans_title",
            "type",
            "url",
            "url_access",
            "url_status",
            "via",
            "volume",
            "website",
            "work",
            "year",
            "zbl",
            "lay_date",
            "lay_format",
            "lay_source",
            "lay_url",
            "transcripturl",
        )
