from typing import Optional

from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import WikipediaPageReference


class CiteEncyclopedia(WikipediaPageReference):
    """This models the template cite encyclopedia in English Wikipedia"""
    last: Optional[str]
    first: Optional[str]
    author_link: Optional[str]
    editor_last: Optional[str]
    editor_first: Optional[str]
    editor_link: Optional[str]
    encyclopedia: Optional[str]
    title: Optional[str]
    trans_title: Optional[str]
    url: Optional[str]
    access_date: Optional[str]
    language: Optional[str]
    edition: Optional[str]
    date: Optional[str]
    year: Optional[str]
    publisher: Optional[str]
    series: Optional[str]
    volume: Optional[str]
    location: Optional[str]
    id: Optional[str]
    isbn: Optional[str]
    oclc: Optional[str]
    doi: Optional[str]
    pages: Optional[str]
    archive_url: Optional[str]
    archive_date: Optional[str]
    url_status: Optional[str]
    quote: Optional[str]
    ref: Optional[str]