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

from config import regex_url_link_extraction
from src.models.api.handlers import BaseHandler
from src.models.api.job.check_url_job import UrlJob
from src.models.api.link.pdf_link import PdfLink
from src.models.exceptions import MissingInformationError

logger = logging.getLogger(__name__)


class PdfHandler(BaseHandler):
    job: UrlJob
    content: bytes = b""
    links_from_original_text: Optional[List[PdfLink]] = None
    links_from_text_without_linebreaks: Optional[List[PdfLink]] = None
    links_from_text_without_spaces: Optional[List[PdfLink]] = None
    annotation_links: Optional[List[PdfLink]] = None
    error: bool = False
    text_pages: Optional[Dict[int, str]] = None
    text_pages_without_linebreaks: Optional[Dict[int, str]] = None
    text_pages_without_spaces: Optional[Dict[int, str]] = None
    url_annotations: Optional[Dict[int, List[Any]]] = None
    error_details: Tuple[int, str] = (0, "")
    file_path: str = ""
    pdf_document: Optional[Document] = None
    word_counts: Optional[List[int]] = None
    # html_pages: Dict[int, str] = {}

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    @property
    def __get_html_output__(self):
        html_pages = {}
        for index, page in enumerate(self.pdf_document.pages()):
            html = page.get_text("html")
            html_pages[index] = html
        return html_pages

    @property
    def __get_xml_output__(self):
        xml_pages = {}
        for index, page in enumerate(self.pdf_document.pages()):
            xml = page.get_text("xml")
            xml_pages[index] = xml
        return xml_pages

    @property
    def __get_json_output__(self):
        json_pages = {}
        for index, page in enumerate(self.pdf_document.pages()):
            json = page.get_text("json")
            json_pages[index] = json
        return json_pages

    @property
    def __get_blocks__(self):
        """Extract blocks of text"""
        block_pages = {}
        for index, page in enumerate(self.pdf_document.pages()):
            raw_blocks = page.get_text("blocks")
            blocks = []
            for block in raw_blocks:
                block_bbox = block[:4]  # Bounding box coordinates
                block_text = block[4]  # Text content
                block_no = block[5]  # Block number
                block_type = block[6]  # Block type
                blocks.append(
                    {
                        "bbox": block_bbox,
                        "text": block_text,
                        "block_no": block_no,
                        "block_type": block_type,
                    }
                )
            block_pages[index] = blocks
        return block_pages

    @property
    def number_of_total_text_characters(self) -> int:
        return len(self.text)

    @property
    def mean_number_of_words_per_page(self) -> int:
        if not self.word_counts:
            self.__count_words__()
        if not self.word_counts:
            return 0
        return round(sum(self.word_counts) / len(self.word_counts))

    @property
    def max_number_of_words_per_page(self) -> int:
        if not self.word_counts:
            self.__count_words__()
        if not self.word_counts:
            return 0
        return max(self.word_counts)

    @property
    def min_number_of_words_per_page(self) -> int:
        if not self.word_counts:
            self.__count_words__()
        if not self.word_counts:
            return 0
        return min(self.word_counts)

    @property
    def number_of_links_from_original_text(self):  # dead: disable
        """Convenience method used in tests"""
        return len(self.links_from_original_text)

    @property
    def number_of_links_from_text_without_linebreaks(self):  # dead: disable
        """Convenience method used in tests"""
        return len(self.links_from_text_without_linebreaks)

    @property
    def number_of_links_from_text_without_spaces(self):  # dead: disable
        """Convenience method used in tests"""
        return len(self.links_from_text_without_spaces)

    @property
    def number_of_links_from_annotations(self):  # dead: disable
        """Convenience method used in tests"""
        return len(self.annotation_links)

    @property
    def number_of_pages(self):
        return self.pdf_document.page_count

    def __count_words__(self) -> None:
        if self.text_pages:
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
        self.text_pages_without_linebreaks = {}
        for index, _ in enumerate(self.text_pages):
            self.text_pages_without_linebreaks[index] = self.__clean_linebreaks__(
                string=self.text_pages[index]
            )

    def __clean_spaces_from_page_text__(self):
        """Clean the page strings and put them into a dictionary attribute"""
        self.text_pages_without_spaces = {}
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
        self.links_from_original_text = []
        if self.text_pages:
            for index, _ in enumerate(self.text_pages):
                # We remove the linebreaks to avoid clipping of URLs, see https://github.com/internetarchive/iari/issues/766
                # provided by chatgpt:
                urls = re.findall(
                    regex_url_link_extraction,
                    self.text_pages[index],
                )
                # cleaned_urls = self.__clean_urls__(urls=urls)
                # valid_urls = self.__discard_invalid_urls__(urls=cleaned_urls)
                for url in urls:
                    if validators.url(url):
                        self.links_from_original_text.append(
                            PdfLink(url=url, page=index)
                        )

    def __extract_links_from_text_without_linebreaks__(self) -> None:
        """Extract all links from the text extract per page"""
        self.links_from_text_without_linebreaks = []
        if self.text_pages_without_linebreaks and self.text_pages:
            for index, _ in enumerate(self.text_pages):
                # We remove the linebreaks to avoid clipping of URLs, see https://github.com/internetarchive/iari/issues/766
                # provided by chatgpt:
                urls = re.findall(
                    regex_url_link_extraction,
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
        self.links_from_text_without_spaces = []
        if self.text_pages:
            for index, _ in enumerate(self.text_pages):
                # We remove the linebreaks to avoid clipping of URLs, see https://github.com/internetarchive/iari/issues/766
                # provided by chatgpt:
                if self.text_pages_without_spaces:
                    urls = re.findall(
                        regex_url_link_extraction,
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
        self.url_annotations = {}
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
        self.annotation_links = []
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
        self.text_pages = {}
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
            "debug_html": self.__get_html_output__,
            "debug_xml": self.__get_xml_output__,
            "debug_json": self.__get_json_output__,
            "debug_blocks": self.__get_blocks__,
            "characters": self.number_of_total_text_characters,
        }
        # console.print(data)
        # exit()
        return data

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
