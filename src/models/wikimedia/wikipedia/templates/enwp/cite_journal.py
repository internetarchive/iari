from typing import Optional

# from src.models.identifier.doi import Doi
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import WikipediaPageReference


class CiteJournal(WikipediaPageReference):
    """This models the template cite journal in English Wikipedia"""
    first: Optional[str]
    last: Optional[str]
    author_link: Optional[str]
    editor_first: Optional[str]
    editor_last: Optional[str]
    editor_link: Optional[str]
    translator_first: Optional[str]
    translator_last: Optional[str]
    translator_link: Optional[str]

    last1: Optional[str]
    first1: Optional[str]
    author_link1: Optional[str]
    last2: Optional[str]
    first2: Optional[str]
    author_link2: Optional[str]
    last3: Optional[str]
    first3: Optional[str]
    author_link3: Optional[str]
    last4: Optional[str]
    first4: Optional[str]
    author_link4: Optional[str]
    last5: Optional[str]
    first5: Optional[str]
    author_link5: Optional[str]
    display_authors: Optional[str]
    author_mask: Optional[str]
    name_list_style: Optional[str]
    date: Optional[str]
    year: Optional[str]
    orig_date: Optional[str]
    editor1_last: Optional[str]
    editor1_first: Optional[str]
    editor1_link: Optional[str]
    editor2_last: Optional[str]
    editor2_first: Optional[str]
    editor2_link: Optional[str]
    editor3_last: Optional[str]
    editor3_first: Optional[str]
    editor3_link: Optional[str]
    editor4_last: Optional[str]
    editor4_first: Optional[str]
    editor4_link: Optional[str]
    editor5_last: Optional[str]
    editor5_first: Optional[str]
    editor5_link: Optional[str]
    display_editors: Optional[str]
    others: Optional[str]
    title: Optional[str]
    script_title: Optional[str]
    trans_title: Optional[str]
    url: Optional[str]
    format: Optional[str]
    department: Optional[str]
    journal: Optional[str]
    type: Optional[str]
    series: Optional[str]
    language: Optional[str]
    edition: Optional[str]
    location: Optional[str]
    publisher: Optional[str]
    publication_place: Optional[str]
    publication_date: Optional[str]
    volume: Optional[str]
    issue: Optional[str]
    page: Optional[str]
    pages: Optional[str]
    at: Optional[str]
    no_pp: Optional[str]
    arxiv: Optional[str]
    asin: Optional[str]
    bibcode: Optional[str]
    biorxiv: Optional[str]
    citeseerx: Optional[str]
    doi: Optional[str]
    doi_broken_date: Optional[str]
    doi_access: Optional[str]
    isbn: Optional[str]
    issn: Optional[str]
    jfm: Optional[str]
    jstor: Optional[str]
    jstor_access: Optional[str]
    lccn: Optional[str]
    mr: Optional[str]
    oclc: Optional[str]
    ol: Optional[str]
    ol_access: Optional[str]
    osti: Optional[str]
    osti_access: Optional[str]
    pmc: Optional[str]
    pmid: Optional[str]
    rfc: Optional[str]
    ssrn: Optional[str]
    zbl: Optional[str]
    id: Optional[str]
    via: Optional[str]
    registration: Optional[str]
    subscription: Optional[str]
    quote: Optional[str]
    postscript: Optional[str]
    ref: Optional[str]
    url_access: Optional[str]
    access_date: Optional[str]
    url_status: Optional[str]
    archive_url: Optional[str]
    archive_date: Optional[str]

    # def __post_init_post_parse__(self):
    #     pass
    # logger: Optional[str] logging.getLogger(__name__)
    # # uGlY hack
    # # Convert after pydantic finished parsing
    # # because it cannot parse into a Doi when given a string.
    # if self.doi: Optional[str]= "":
    #     self.doi: Optional[str] None
    # else:
    #     self.doi: Doi: Optional[str] Doi(value=self.doi)
    # logger.warning("post init post parse was run")

    # def __parse_template__(self):
    #     logger: Optional[str] logging.getLogger(__name__)
    #     for key, value in self.content.items():
    #         if key: Optional[str]= "doi":
    #             logger.info(f"Found doi: {value}")
    #             self.doi: Optional[str] Doi(value)
    #         if key: Optional[str]= "journal_title":
    #             logger.info(f"Found journal_title: {value}")
    #             # Todo decide about how to handle the [[]] of this value
    #             # Could we get the QID for the journal_title?
    #             self.journal_title: Optional[str] value
    #         if key: Optional[str]= "jstor":
    #             logger.info(f"Found jstor: {value}")
    #             self.jstor: Optional[str] value
    #         if key: Optional[str]= "pmid":
    #             logger.info(f"Found pmid: {value}")
    #             self.pmid: Optional[str] value
    #         if key: Optional[str]= "title":
    #             logger.info(f"Found title: {value}")
    #             self.article_title: Optional[str] value

    def __str__(self):
        return f"<[bold green]{self.title}[/bold green] (doi:{self.doi} pmid:{self.pmid} jstor:{self.jstor})>"
