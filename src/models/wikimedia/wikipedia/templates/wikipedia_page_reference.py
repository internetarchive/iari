import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator, Field

logger = logging.getLogger(__name__)

# We use marshmallow here because pydantic did not seem to support optional alias fields.
# https://github.com/samuelcolvin/pydantic/discussions/3855


class WikipediaPageReference(BaseModel):
    """This models any reference on a Wikipedia page

    Do we want to merge page + pages into a string property like in Wikidata?
    How do we handle parse errors? In a file log? Should we publish the log for Wikipedians to fix?

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
    author_given: Optional[str] = Field(..., alias="author-given")
    author_given1: Optional[str] = Field(..., alias="author-given1")
    author_given2: Optional[str] = Field(..., alias="author-given2")
    author_given3: Optional[str] = Field(..., alias="author-given3")
    author_given4: Optional[str] = Field(..., alias="author-given4")
    author_given5: Optional[str] = Field(..., alias="author-given5")
    author_first: Optional[str] = Field(..., alias="author-first")
    author_first1: Optional[str] = Field(..., alias="author-first1")
    author_first2: Optional[str] = Field(..., alias="author-first2")
    author_first3: Optional[str] = Field(..., alias="author-first3")
    author_first4: Optional[str] = Field(..., alias="author-first4")
    author_first5: Optional[str] = Field(..., alias="author-first5")

    #######################
    # Author last/surname (equal)
    #######################
    author_surname: Optional[str] = Field(..., alias="author-surname")
    author_surname1: Optional[str] = Field(..., alias="author-surname1")
    author_surname2: Optional[str] = Field(..., alias="author-surname2")
    author_surname3: Optional[str] = Field(..., alias="author-surname3")
    author_surname4: Optional[str] = Field(..., alias="author-surname4")
    author_surname5: Optional[str] = Field(..., alias="author-surname5")
    author_last: Optional[str] = Field(..., alias="author-last")
    author_last1: Optional[str] = Field(..., alias="author-last1")
    author_last2: Optional[str] = Field(..., alias="author-last2")
    author_last3: Optional[str] = Field(..., alias="author-last3")
    author_last4: Optional[str] = Field(..., alias="author-last4")
    author_last5: Optional[str] = Field(..., alias="author-last5")

    # Author
    author: Optional[str]
    author_link1: Optional[str] = Field(..., alias="author-link1")
    author_link2: Optional[str] = Field(..., alias="author-link2")
    author_link3: Optional[str] = Field(..., alias="author-link3")
    author_link4: Optional[str] = Field(..., alias="author-link4")
    author_link5: Optional[str] = Field(..., alias="author-link5")
    author_link: Optional[str] = Field(..., alias="author-link")
    author_mask1: Optional[str] = Field(..., alias="author-mask1")
    author_mask2: Optional[str] = Field(..., alias="author-mask2")
    author_mask3: Optional[str] = Field(..., alias="author-mask3")
    author_mask4: Optional[str] = Field(..., alias="author-mask4")
    author_mask5: Optional[str] = Field(..., alias="author-mask5")
    author_mask: Optional[str] = Field(..., alias="author-mask")

    #######################
    # Editor
    #######################
    editor1_first: Optional[str] = Field(..., alias="editor1-first")
    editor1_last: Optional[str] = Field(..., alias="editor1-last")
    editor1_link: Optional[str] = Field(..., alias="editor1-link")
    editor2_first: Optional[str] = Field(..., alias="editor2-first")
    editor2_last: Optional[str] = Field(..., alias="editor2-last")
    editor2_link: Optional[str] = Field(..., alias="editor2-link")
    editor3_first: Optional[str] = Field(..., alias="editor3-first")
    editor3_last: Optional[str] = Field(..., alias="editor3-last")
    editor3_link: Optional[str] = Field(..., alias="editor3-link")
    editor4_first: Optional[str] = Field(..., alias="editor4-first")
    editor4_last: Optional[str] = Field(..., alias="editor4-last")
    editor4_link: Optional[str] = Field(..., alias="editor4-link")
    editor5_first: Optional[str] = Field(..., alias="editor5-first")
    editor5_last: Optional[str] = Field(..., alias="editor5-last")
    editor5_link: Optional[str] = Field(..., alias="editor5-link")
    editor: Optional[str]
    editor_first1: Optional[str] = Field(..., alias="editor-first1")
    editor_first2: Optional[str] = Field(..., alias="editor-first2")
    editor_first3: Optional[str] = Field(..., alias="editor-first3")
    editor_first4: Optional[str] = Field(..., alias="editor-first4")
    editor_first5: Optional[str] = Field(..., alias="editor-first5")
    editor_first: Optional[str] = Field(..., alias="editor-first")
    editor_last1: Optional[str] = Field(..., alias="editor-last1")
    editor_last2: Optional[str] = Field(..., alias="editor-last2")
    editor_last3: Optional[str] = Field(..., alias="editor-last3")
    editor_last4: Optional[str] = Field(..., alias="editor-last4")
    editor_last5: Optional[str] = Field(..., alias="editor-last5")
    editor_last: Optional[str] = Field(..., alias="editor-last")
    editor_link1: Optional[str] = Field(..., alias="editor-link1")
    editor_link2: Optional[str] = Field(..., alias="editor-link2")
    editor_link3: Optional[str] = Field(..., alias="editor-link3")
    editor_link4: Optional[str] = Field(..., alias="editor-link4")
    editor_link5: Optional[str] = Field(..., alias="editor-link5")
    editor_link: Optional[str] = Field(..., alias="editor-link")
    editor_mask1: Optional[str] = Field(..., alias="editor-mask1")
    editor_mask2: Optional[str] = Field(..., alias="editor-mask2")
    editor_mask3: Optional[str] = Field(..., alias="editor-mask3")
    editor_mask4: Optional[str] = Field(..., alias="editor-mask4")
    editor_mask5: Optional[str] = Field(..., alias="editor-mask5")
    editor_mask: Optional[str] = Field(..., alias="editor-mask")

    #######################
    # Translator
    #######################
    translator_first1: Optional[str] = Field(..., alias="translator-first1")
    translator_first2: Optional[str] = Field(..., alias="translator-first2")
    translator_first3: Optional[str] = Field(..., alias="translator-first3")
    translator_first4: Optional[str] = Field(..., alias="translator-first4")
    translator_first5: Optional[str] = Field(..., alias="translator-first5")
    translator_first: Optional[str] = Field(..., alias="translator-first")
    translator_last1: Optional[str] = Field(..., alias="translator-last1")
    translator_last2: Optional[str] = Field(..., alias="translator-last2")
    translator_last3: Optional[str] = Field(..., alias="translator-last3")
    translator_last4: Optional[str] = Field(..., alias="translator-last4")
    translator_last5: Optional[str] = Field(..., alias="translator-last5")
    translator_last: Optional[str] = Field(..., alias="translator-last")
    translator_link1: Optional[str] = Field(..., alias="translator-link1")
    translator_link2: Optional[str] = Field(..., alias="translator-link2")
    translator_link3: Optional[str] = Field(..., alias="translator-link3")
    translator_link4: Optional[str] = Field(..., alias="translator-link4")
    translator_link5: Optional[str] = Field(..., alias="translator-link5")
    translator_link: Optional[str] = Field(..., alias="translator-link")
    translator_mask1: Optional[str] = Field(..., alias="translator-mask1")
    translator_mask2: Optional[str] = Field(..., alias="translator-mask2")
    translator_mask3: Optional[str] = Field(..., alias="translator-mask3")
    translator_mask4: Optional[str] = Field(..., alias="translator-mask4")
    translator_mask5: Optional[str] = Field(..., alias="translator-mask5")
    translator_mask: Optional[str] = Field(..., alias="translator-mask")

    #######################
    # Interviewer
    #######################
    interviewer_given: Optional[str] = Field(..., alias="interviewer-given")
    interviewer_first: Optional[str] = Field(..., alias="interviewer-first")
    interviewer_surname: Optional[str] = Field(..., alias="interviewer-surname")
    interviewer_last: Optional[str] = Field(..., alias="interviewer-last")

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
    access_date: Optional[datetime] = Field(..., alias="access-date")
    agency: Optional[str]  # what is this?
    archive_date: Optional[datetime] = Field(..., alias="archive-date")
    archive_url: Optional[str] = Field(..., alias="archive-url")
    arxiv: Optional[str]
    asin: Optional[str]  # what is this?
    asin_tld: Optional[str] = Field(..., alias="asin_tld")  # what is this?
    at: Optional[str]  # what is this?
    bibcode: Optional[str]
    bibcode_access: Optional[str] = Field(..., alias="bibcode-access")
    biorxiv: Optional[str]
    book_title: Optional[str] = Field(..., alias="book-title")
    chapter: Optional[str]
    chapter_format: Optional[str] = Field(..., alias="chapter-format")
    chapter_url: Optional[str] = Field(..., alias="chapter-url")
    chapter_url_access: Optional[str] = Field(..., alias="chapter-url-access")
    citeseerx: Optional[str]
    news_class: Optional[str]  # used in cite arxiv
    conference: Optional[str]
    conference_url: Optional[str] = Field(..., alias="conference-url")
    date: Optional[datetime]
    degree: Optional[str]
    department: Optional[str]
    doi: Optional[str]
    doi_access: Optional[str] = Field(..., alias="doi-access")
    doi_broken_date: Optional[datetime] = Field(..., alias="doi-broken-date")
    edition: Optional[str]
    eissn: Optional[str]
    encyclopedia: Optional[str]
    eprint: Optional[str]
    format: Optional[str]
    hdl: Optional[str]
    hdl_access: Optional[str] = Field(..., alias="hdl-access")
    id: Optional[str]  # where does this come from?
    isbn: Optional[str]
    ismn: Optional[str]
    issn: Optional[str]
    issue: Optional[str]
    jfm: Optional[str]
    journal: Optional[str]
    jstor: Optional[str]
    jstor_access: Optional[str] = Field(..., alias="jstor-access")
    language: Optional[str]  # do we want to parse this?
    lccn: Optional[str]
    location: Optional[str]
    mode: Optional[str]  # what is this?
    mr: Optional[str]
    name_list_style: Optional[str] = Field(..., alias="name-list-style")
    no_pp: Optional[str] = Field(..., alias="no-pp")
    oclc: Optional[str]
    ol: Optional[str]  # what is this?
    ol_access: Optional[str] = Field(..., alias="ol-access")  # what is this?
    orig_date: Optional[datetime] = Field(..., alias="orig-date")
    osti: Optional[str]  # what is this?
    osti_access: Optional[str] = Field(..., alias="osti-access")  # what is this?
    others: Optional[str]  # what is this?
    page: Optional[str]
    pages: Optional[str]
    pmc: Optional[str]
    pmc_embargo_date: Optional[datetime] = Field(..., alias="pmc-embargo-date")
    pmid: Optional[str]
    postscript: Optional[str]  # what is this?
    publication_date: Optional[datetime] = Field(..., alias="publication-date")
    publication_place: Optional[str] = Field(..., alias="publication-place")
    publisher: Optional[str]
    quote: Optional[str]  # do we want to store this?
    quote_page: Optional[str] = Field(..., alias="quote-page")
    quote_pages: Optional[str] = Field(..., alias="quote-pages")
    ref: Optional[str]
    registration: Optional[str]  # what is this?
    rfc: Optional[str]  # what is this?
    s2cid: Optional[str]
    s2cid_access: Optional[str] = Field(..., alias="s2cid-access")
    sbn: Optional[str]
    script_chapter: Optional[str] = Field(..., alias="script-chapter")
    script_quote: Optional[str] = Field(..., alias="script-quote")
    script_title: Optional[str] = Field(..., alias="script-title")
    series: Optional[str]
    ssrn: Optional[str]
    subject: Optional[str]
    subject_mask: Optional[str] = Field(..., alias="subject-mask")
    subscription: Optional[str]
    title: Optional[str]
    title_link: Optional[str] = Field(..., alias="title-link")
    trans_chapter: Optional[str] = Field(
        ..., alias="trans-chapter"
    )  # this is a translation of a chapter
    trans_quote: Optional[str] = Field(
        ..., alias="trans-quote"
    )  # this is a translation of a quote
    trans_title: Optional[str] = Field(
        ..., alias="trans-title"
    )  # this is a translation of a title
    type: Optional[str]  # what is this?
    url: Optional[str] = Field(..., alias="1")
    url_access: Optional[str] = Field(..., alias="url-access")
    url_status: Optional[str] = Field(..., alias="url-staus")
    via: Optional[str]  # what is this?
    volume: Optional[str]
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

    class Config:
        extra = "forbid"
        allow_population_by_field_name = True

    @validator(
        "access_date",
        "archive_date",
        "date",
        "doi_broken_date",
        "orig_date",
        "pmc_embargo_date",
        "publication_date",
        pre=True,
    )
    def time_validate(cls, v):
        """Pydantic validator
        see https://stackoverflow.com/questions/66472255/"""
        date = None
        # Supported "2019-03-22"
        try:
            date = datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            pass
        # Supported "19-03-22"
        # try:
        #     date = datetime.strptime(v, "%y-%m-%d")
        # except ValueError:
        #     pass
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
            date = datetime.strptime(v, "%b %Y")
        except ValueError:
            pass
        # Support "May 9, 2013a"
        try:
            date = datetime.strptime(v[:-1], "%B %d, %Y")
        except ValueError:
            pass
        # Support "Jul 9, 2013a"
        try:
            date = datetime.strptime(v[:-1], "%b %d, %Y")
        except ValueError:
            pass
        # Support "2017"
        try:
            date = datetime.strptime(v, "%Y")
        except ValueError:
            pass
        # Support "Summer 2013"
        try:
            # We strip the vague part and just keep the year.
            date = datetime.strptime(
                v.lower()
                .replace("spring", "")
                .replace("summer", "")
                .replace("autumn", "")
                .replace("winter", "")
                .strip(),
                "%Y",
            )
        except ValueError:
            pass
        if date is None:
            logger.warning(f"date format '{v}' not supported yet")
            return None
        return date
