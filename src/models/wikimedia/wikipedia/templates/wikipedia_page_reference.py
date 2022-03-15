import logging
from datetime import datetime
from typing import Optional

from marshmallow import (
    Schema,
)
from marshmallow.fields import String
from pydantic import BaseModel, validator

from src.models.exceptions import TimeParseException

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

    # We use this to keep track of which template the information came from
    template_name: str

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
    first: Optional[str]
    last1: Optional[str]
    last2: Optional[str]
    last3: Optional[str]
    last4: Optional[str]
    last5: Optional[str]
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

    @validator(
        "access_date",
        "archive_date",
        "date",
        "doi_broken_date",
        "orig_date",
        "orig_year",
        "pmc_embargo_date",
        "publication_date",
        pre=True,
    )
    def validate_time(cls, v):
        """Pydantic validator
        see https://stackoverflow.com/questions/66472255/"""
        date = None
        try:
            date = datetime.strptime(v, "%y-%m-%d")
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
        # Support "1 September 2003"
        try:
            date = datetime.strptime(v, "%d %B %Y")
        except ValueError:
            pass
        # Support "September 2003"
        try:
            date = datetime.strptime(v, "%B %Y")
        except ValueError:
            pass
        # Support "Sep 2003"
        try:
            date = datetime.strptime(v, "%B %Y")
        except ValueError:
            pass
        if date is None:
            raise TimeParseException(f"date format '{v}' not supported yet")
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
            # dates
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
            "first",
            "last1",
            "last2",
            "last3",
            "last4",
            "last5",
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
        ordered = True
