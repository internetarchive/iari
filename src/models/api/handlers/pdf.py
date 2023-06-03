import logging
import re
from copy import deepcopy
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

import fitz  # type: ignore
import requests
import validators  # type: ignore
from fitz import (
    Document,  # type: ignore
    FileDataError,
)

# type: ignore
from requests import ReadTimeout

from config import link_extraction_regex
from src.models.api.handlers import BaseHandler
from src.models.api.job.check_url_job import UrlJob
from src.models.api.link.pdf_link import PdfLink
from src.models.exceptions import MissingInformationError

logger = logging.getLogger(__name__)


class PdfHandler(BaseHandler):
    job: UrlJob
    content: bytes = b""
    links_from_original_text: List[PdfLink] = []
    links_from_text_without_linebreaks: List[PdfLink] = []
    links_from_text_without_spaces: List[PdfLink] = []
    annotation_links: List[PdfLink] = []
    error: bool = False
    text_pages: Dict[int, str] = {}
    text_pages_without_linebreaks: Dict[int, str] = {}
    text_pages_without_spaces: Dict[int, str] = {}
    url_annotations: Dict[int, List[Any]] = {}
    error_details: Tuple[int, str] = (0, "")
    # urls_fixed: List[str] = []
    file_path: str = ""
    pdf_document: Optional[Document] = None
    word_counts: List[int] = []
    # html_pages: Dict[int, str] = {}

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    @property
    def number_of_total_text_characters(self) -> int:
        return len(self.text)

    @property
    def mean_number_of_words_per_page(self) -> int:
        if not self.word_counts:
            self.__count_words__()
        return round(sum(self.word_counts) / len(self.word_counts))

    @property
    def max_number_of_words_per_page(self) -> int:
        if not self.word_counts:
            self.__count_words__()
        return max(self.word_counts)

    @property
    def min_number_of_words_per_page(self) -> int:
        if not self.word_counts:
            self.__count_words__()
        return min(self.word_counts)

    # @property
    # def number_of_links_from_original_text(self):
    #     return len(self.links_from_original_text)
    #
    # @property
    # def number_of_links_from_text_without_linebreaks(self):
    #     return len(self.links_from_text_without_linebreaks)
    #
    # @property
    # def number_of_links_from_text_without_spaces(self):
    #     return len(self.links_from_text_without_spaces)

    # @property
    # def number_of_annotation_links(self):
    #     return len(self.annotation_links)

    @property
    def number_of_pages(self):
        return self.pdf_document.page_count

    def __count_words__(self) -> None:
        self.word_counts = [
            len(page_text.split()) for page_text in self.text_pages.values()
        ]

    def __download_pdf__(self):
        """Download PDF file from URL"""
        from src import app

        app.logger.debug("__download_pdf__: running")
        if not self.content:
            try:
                response = requests.get(self.job.url, timeout=self.job.timeout)
                if response.content:
                    self.content = response.content
                else:
                    # We got a response but there is no content to work on
                    self.error = True
                    self.error_details = (
                        400,
                        (
                            f"Got status code {response.status_code} but no "
                            f"content from the URL"
                        ),
                    )
                    logger.warning(self.error_details)
            except ReadTimeout:
                self.error = True
                self.error_details = (
                    404,
                    f"Got a ReadTimeout when trying to reach the url {self.job.url}",
                )
                logger.warning(self.error_details)

    def __clean_linebreaks_from_page_text__(self):
        """Clean the page strings and put them into a dictionary attribute"""
        for index, _ in enumerate(self.text_pages):
            self.text_pages_without_linebreaks[index] = self.__clean_linebreaks__(
                string=self.text_pages[index]
            )

    def __clean_spaces_from_page_text__(self):
        """Clean the page strings and put them into a dictionary attribute"""
        for index, _ in enumerate(self.text_pages):
            self.text_pages_without_spaces[index] = self.__clean_spaces__(
                string=self.text_pages[index]
            )

    # def __extract_links_from_html__(self) -> None:
    #     """Extract all links from the html extract per page"""
    #     for index, _ in enumerate(self.html_pages):
    #         xhtml = XhtmlHandler(content=self.html_pages[index])
    #         xhtml.__parse_into_soup__()
    #         xhtml.__extract_links__()
    #         print(xhtml.links)
    #         # for url in urls:
    #         #     if validators.url(url):
    #         #         self.all_text_links.append(PdfLink(url=url, page=index))

    def __extract_links_from_original_text__(self) -> None:
        """Extract all links from the text extract per page"""
        for index, _ in enumerate(self.text_pages):
            # We remove the linebreaks to avoid clipping of URLs, see https://github.com/internetarchive/iari/issues/766
            # provided by chatgpt:
            urls = re.findall(
                link_extraction_regex,
                self.text_pages[index],
            )
            # cleaned_urls = self.__clean_urls__(urls=urls)
            # valid_urls = self.__discard_invalid_urls__(urls=cleaned_urls)
            for url in urls:
                if validators.url(url):
                    self.links_from_original_text.append(PdfLink(url=url, page=index))

    def __extract_links_from_text_without_linebreaks__(self) -> None:
        """Extract all links from the text extract per page"""
        for index, _ in enumerate(self.text_pages):
            # We remove the linebreaks to avoid clipping of URLs, see https://github.com/internetarchive/iari/issues/766
            # provided by chatgpt:
            urls = re.findall(
                link_extraction_regex,
                self.text_pages_without_linebreaks[index],
            )
            # cleaned_urls = self.__clean_urls__(urls=urls)
            # valid_urls = self.__discard_invalid_urls__(urls=cleaned_urls)
            for url in urls:
                if validators.url(url):
                    self.links_from_text_without_linebreaks.append(
                        PdfLink(url=url, page=index)
                    )

    def __extract_links_from_text_without_spaces__(self) -> None:
        """Extract all links from the text extract per page"""
        for index, _ in enumerate(self.text_pages):
            # We remove the linebreaks to avoid clipping of URLs, see https://github.com/internetarchive/iari/issues/766
            # provided by chatgpt:
            urls = re.findall(
                link_extraction_regex,
                self.text_pages_without_spaces[index],
            )
            # cleaned_urls = self.__clean_urls__(urls=urls)
            # valid_urls = self.__discard_invalid_urls__(urls=cleaned_urls)
            for url in urls:
                if validators.url(url):
                    self.links_from_text_without_spaces.append(
                        PdfLink(url=url, page=index)
                    )

    def __get_annotations__(self):
        """Extract the raw annotations into an attribute dictionary"""
        if not self.pdf_document:
            raise MissingInformationError()
        for page_num in range(self.pdf_document.page_count):
            page = self.pdf_document.load_page(page_num)
            # todo is this zero based?
            all_annotations = page.get_links()
            url_annotations = []
            for annotation in all_annotations:
                if annotation["kind"] == fitz.LINK_URI:
                    # We remove Rect() here because it is not understood by the json encoder
                    cleaned_annotation = deepcopy(annotation)
                    if cleaned_annotation["from"]:
                        cleaned_annotation["from"] = str(cleaned_annotation["from"])
                    url_annotations.append(cleaned_annotation)
            # print(type(annotations))
            # console.print(annotations)
            # exit()
            if url_annotations:
                self.url_annotations[page_num] = url_annotations

    def __extract_links_from_annotations__(self) -> None:
        if not self.pdf_document:
            raise MissingInformationError()
        for page_num in range(self.pdf_document.page_count):
            page = self.pdf_document.load_page(page_num)
            annotations = page.get_links()
            for annotation in annotations:
                # print(annotation)
                if annotation["kind"] == fitz.LINK_URI:
                    url = annotation["uri"]
                    if validators.url(url):
                        self.annotation_links.append(PdfLink(url=url, page=page_num))

    def __extract_text_pages__(self) -> None:
        """Extract all text from all pages"""
        if not self.pdf_document:
            self.__extract_pdf_document__()
        if not self.pdf_document:
            raise MissingInformationError()
        for index, page in enumerate(self.pdf_document.pages()):
            # See https://pymupdf.readthedocs.io/en/latest/app1.html
            text = page.get_text("text")
            self.text_pages[index] = text

    # def __extract_html_pages__(self) -> None:
    #     """Extract all text from all pages"""
    #     if not self.pdf_document:
    #         self.__extract_pdf_document__()
    #     if not self.pdf_document:
    #         raise MissingInformationError()
    #     for index, page in enumerate(self.pdf_document.pages()):
    #         # See https://pymupdf.readthedocs.io/en/latest/app1.html
    #         html = page.get_text("html")
    #         self.html_pages[index] = html

    def __extract_pdf_document__(self):
        if not self.content:
            raise MissingInformationError()
        with BytesIO(self.content) as pdf_file:
            try:
                # noinspection PyUnresolvedReferences
                self.pdf_document = Document(stream=pdf_file.read(), filetype="pdf")
            except FileDataError:
                self.error = True
                self.error_details = (415, "Not a valid PDF according to PyMuPDF")
                logger.error(self.error_details)

    def download_and_extract(self):
        self.__download_pdf__()
        self.__extract_pages_and_links__()

    def read_and_extract(self):  # dead: disable
        self.__read_pdf_from_file__()
        self.__extract_pages_and_links__()

    def get_dict(self):
        """Return data to the patron"""
        links_from_original_text = [
            link.dict() for link in self.links_from_original_text
        ]
        links_from_text_without_linebreaks = [
            link.dict() for link in self.links_from_text_without_linebreaks
        ]
        links_from_text_without_spaces = [
            link.dict() for link in self.links_from_text_without_spaces
        ]
        annotation_links = [link.dict() for link in self.annotation_links]
        data = {
            "words_mean": self.mean_number_of_words_per_page,
            "words_max": self.max_number_of_words_per_page,
            "words_min": self.min_number_of_words_per_page,
            "annotation_links": annotation_links,
            "links_from_original_text": links_from_original_text,
            "links_from_text_without_linebreaks": links_from_text_without_linebreaks,
            "links_from_text_without_spaces": links_from_text_without_spaces,
            "url": self.job.url,
            "timeout": self.job.timeout,
            "pages_total": self.number_of_pages,
            "detected_language": self.detected_language,
            "detected_language_error": self.detected_language_error,
            "detected_language_error_details": self.detected_language_error_details,
            "debug_text_original": self.text_pages,
            "debug_text_without_linebreaks": self.text_pages_without_linebreaks,
            "debug_text_without_spaces": self.text_pages_without_spaces,
            "debug_url_annotations": self.url_annotations,
            "characters": self.number_of_total_text_characters,
        }
        # console.print(data)
        # exit()
        return data

    # def __get_cleaned_page_string__(self, number) -> str:
    #     page_string = self.text_pages[number]
    #     page_string = self.__clean_linebreaks__(string=page_string)
    #     return page_string

    # def __fix_doi_typing_errors__(self, string):
    #     """This fixes common typing errors that we found"""
    #     # From https://s3.documentcloud.org/documents/23782225/mwg-fdr-document-04-16-23-1.pdf page 298
    #     if "https://doi.org:" in string:
    #         self.urls_fixed.append("https://doi.org:")
    #         string = string.replace("https://doi.org:", "https://doi.org/")
    #     # From https://s3.documentcloud.org/documents/23782225/mwg-fdr-document-04-16-23-1.pdf page 298
    #     if "https://doi.or/" in string:
    #         self.urls_fixed.append("https://doi.or/")
    #         string = string.replace("https://doi.or/", "https://doi.org/")
    #     return string

    def __read_pdf_from_file__(self):
        """This is needed for fast testing on pdfs in test_data"""
        with open(self.file_path, "rb") as file:
            self.content = file.read()

    def __extract_pages_and_links__(self):
        from src import app

        app.logger.debug("__extract_pages_and_links__: running")
        if not self.error:
            self.__extract_pdf_document__()
        if not self.error:
            self.__get_annotations__()
            self.__extract_links_from_annotations__()
        if not self.error:
            self.__clean_and_extract_links_from_text__()
        self.__concatenate_text_from_all_pages__()
        self.__detect_language__()

    @staticmethod
    def __clean_linebreaks__(string: str):
        for char in ["\n", "\r", "\v", "\f", "\u2028", "\u2029"]:
            string = string.replace(char, "")
        return string

    @staticmethod
    def __clean_spaces__(string: str):
        for char in [" "]:
            string = string.replace(char, "")
        return string

    def __concatenate_text_from_all_pages__(self):
        """This is needed for language detection"""
        for index, _ in enumerate(self.text_pages):
            self.text += self.text_pages[index]

    def __clean_and_extract_links_from_text__(self):
        """Helper method"""
        self.__extract_text_pages__()
        self.__clean_linebreaks_from_page_text__()
        self.__clean_spaces_from_page_text__()
        self.__extract_links_from_original_text__()
        self.__extract_links_from_text_without_linebreaks__()
        self.__extract_links_from_text_without_spaces__()
