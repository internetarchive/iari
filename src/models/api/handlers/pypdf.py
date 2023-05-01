import logging
import re
from io import BytesIO
from typing import Dict, List

import fitz  # type: ignore
import requests
from fitz import FileDataError
from pydantic import BaseModel

from src.models.api.job.check_url_job import UrlJob
from src.models.api.link.pdf_link import PdfLink
from src.models.exceptions import MissingInformationError

logger = logging.getLogger(__name__)


class PdfHandler(BaseModel):
    job: UrlJob
    content: bytes = b""
    links: List[PdfLink] = []
    error: bool = False
    pages: Dict[int, str] = {}
    error_details: str = ""
    urls_fixed: List[str] = []
    file_path: str = ""

    @property
    def number_of_links(self):
        return len(self.links)

    @property
    def number_of_pages(self):
        return len(self.pages)

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

    def __extract_links__(self) -> None:
        """Extract all links from the text extract per page"""
        for index, _ in enumerate(self.pages):
            # We remove the linebreaks to avoid clipping of URLs, see https://github.com/internetarchive/iari/issues/766
            # provided by chatgpt:
            regex = r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?"
            urls = re.findall(regex, self.__get_cleaned_page_string__(number=index))
            # cleaned_urls = self.__clean_urls__(urls=urls)
            # valid_urls = self.__discard_invalid_urls__(urls=cleaned_urls)
            for url in urls:
                self.links.append(PdfLink(url=url, page=index))

    def __extract_pages_using_pymupdf__(self) -> None:
        """Extract all text from all pages"""
        if not self.content:
            raise MissingInformationError()
        with BytesIO(self.content) as pdf_file:
            try:
                # noinspection PyUnresolvedReferences
                pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
                for index, page in enumerate(pdf_document.pages()):
                    text = page.get_text()
                    self.pages[index] = text
            except FileDataError:
                self.error = True
                self.error_details = "Not a valid PDF according to PyMuPDF"
                logger.error(self.error_details)

    def download_and_extract(self):
        self.__download_pdf__()
        self.__extract_pages_and_links__()

    def get_dict(self):
        """Return data to the patron"""
        links = [link.dict() for link in self.links]
        if self.urls_fixed:
            return dict(
                links=links,
                links_total=self.number_of_links,
                url=self.job.url,
                timeout=self.job.timeout,
                urls_fixed=self.urls_fixed,
                pages_total=self.number_of_pages,
            )
        else:
            return dict(
                links=links,
                links_total=self.number_of_links,
                url=self.job.url,
                timeout=self.job.timeout,
                urls_fixed=None,
            )

    def __get_cleaned_page_string__(self, number) -> str:
        page_string = self.pages[number]
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
            # self.__extract_pages_using_pypdf__()
            self.__extract_pages_using_pymupdf__()
        if not self.error:
            self.__extract_links__()

    @staticmethod
    def __clean_linebreaks__(string):
        for char in ["\n", "\r", "\v", "\f", "\u2028", "\u2029"]:
            string = string.replace(char, "")
        return string
