import logging
import re
from io import BytesIO
from typing import Dict, List, Optional

import fitz  # type: ignore
import requests
from fitz import (
    Document,  # type: ignore
    FileDataError,  # type: ignore
)
from pydantic import BaseModel

from src.models.api.job.check_url_job import UrlJob
from src.models.api.link.pdf_link import PdfLink
from src.models.exceptions import MissingInformationError

logger = logging.getLogger(__name__)


class PdfHandler(BaseModel):
    job: UrlJob
    content: bytes = b""
    all_text_links: List[PdfLink] = []
    annotation_links: List[PdfLink] = []
    error: bool = False
    text_pages: Dict[int, str] = {}
    error_details: str = ""
    urls_fixed: List[str] = []
    file_path: str = ""
    pdf_document: Optional[Document] = None

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    @property
    def number_of_text_links(self):
        return len(self.all_text_links)

    @property
    def number_of_annotation_links(self):
        return len(self.annotation_links)

    @property
    def number_of_pages(self):
        return self.pdf_document.page_count

    def __download_pdf__(self):
        """Download PDF file from URL"""
        if not self.content:
            response = requests.get(self.job.url, timeout=self.job.timeout)
            if response.content:
                self.content = response.content
            else:
                self.error = True
                self.error_details = (
                    f"Got no content from URL using "
                    f"requests and timeout {self.job.timeout}"
                )
                logger.warning(self.error_details)

    def __extract_links_from_all_text__(self) -> None:
        """Extract all links from the text extract per page"""
        for index, _ in enumerate(self.text_pages):
            # We remove the linebreaks to avoid clipping of URLs, see https://github.com/internetarchive/iari/issues/766
            # provided by chatgpt:
            regex = r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?"
            urls = re.findall(regex, self.__get_cleaned_page_string__(number=index))
            # cleaned_urls = self.__clean_urls__(urls=urls)
            # valid_urls = self.__discard_invalid_urls__(urls=cleaned_urls)
            for url in urls:
                self.all_text_links.append(PdfLink(url=url, page=index))

    def __extract_links_from_annotations__(self) -> None:
        if not self.pdf_document:
            raise MissingInformationError()
        for page_num in range(self.pdf_document.page_count):
            page = self.pdf_document.load_page(page_num)
            annotations = page.get_links()
            for annotation in annotations:
                # print(annotation)
                if annotation["kind"] == fitz.LINK_URI:
                    self.annotation_links.append(
                        PdfLink(url=annotation["uri"], page=page_num)
                    )

    def __extract_text_pages__(self) -> None:
        """Extract all text from all pages"""
        if not self.pdf_document:
            raise MissingInformationError()
        for index, page in enumerate(self.pdf_document.pages()):
            text = page.get_text()
            self.text_pages[index] = text

    def __extract_pdf_document__(self):
        if not self.content:
            raise MissingInformationError()
        with BytesIO(self.content) as pdf_file:
            try:
                # noinspection PyUnresolvedReferences
                self.pdf_document = Document(stream=pdf_file.read(), filetype="pdf")
            except FileDataError:
                self.error = True
                self.error_details = "Not a valid PDF according to PyMuPDF"
                logger.error(self.error_details)

    def download_and_extract(self):
        self.__download_pdf__()
        self.__extract_pages_and_links__()

    def get_dict(self):
        """Return data to the patron"""
        text_links = [link.dict() for link in self.all_text_links]
        annotation_links = [link.dict() for link in self.annotation_links]
        if self.urls_fixed:
            return dict(
                annotation_links=annotation_links,
                text_links=text_links,
                text_links_total=self.number_of_text_links,
                annotation_links_total=self.number_of_annotation_links,
                url=self.job.url,
                timeout=self.job.timeout,
                urls_fixed=self.urls_fixed,
                pages_total=self.number_of_pages,
            )
        else:
            return dict(
                annotation_links=annotation_links,
                text_links=text_links,
                text_links_total=self.number_of_text_links,
                annotation_links_total=self.number_of_annotation_links,
                url=self.job.url,
                timeout=self.job.timeout,
                urls_fixed=None,
            )

    def __get_cleaned_page_string__(self, number) -> str:
        page_string = self.text_pages[number]
        page_string = self.__clean_linebreaks__(string=page_string)
        page_string = self.__fix_doi_typing_errors__(string=page_string)
        return page_string

    def __fix_doi_typing_errors__(self, string):
        """This fixes common typing errors that we found"""
        # From https://s3.documentcloud.org/documents/23782225/mwg-fdr-document-04-16-23-1.pdf page 298
        if "https://doi.org:" in string:
            self.urls_fixed.append("https://doi.org:")
            string = string.replace("https://doi.org:", "https://doi.org/")
        # From https://s3.documentcloud.org/documents/23782225/mwg-fdr-document-04-16-23-1.pdf page 298
        if "https://doi.or/" in string:
            self.urls_fixed.append("https://doi.or/")
            string = string.replace("https://doi.or/", "https://doi.org/")
        return string

    def read_pdf_from_file(self):  # dead: disable
        """This is needed for fast testing on pdfs in test_data"""
        with open(self.file_path, "rb") as file:
            self.content = file.read()

    def __extract_pages_and_links__(self):
        if not self.error:
            self.__extract_pdf_document__()
        if not self.error:
            self.__extract_links_from_annotations__()
            self.__extract_text_pages__()
        if not self.error:
            self.__extract_links_from_all_text__()

    @staticmethod
    def __clean_linebreaks__(string):
        for char in ["\n", "\r", "\v", "\f", "\u2028", "\u2029"]:
            string = string.replace(char, "")
        return string
