# from io import BytesIO
# from typing import List, Optional
#
# import requests
# from pdfx import PDFMinerBackend
# from pydantic import BaseModel
#
# from src.models.api.job.check_url_job import UrlJob
# from src.models.exceptions import MissingInformationError
#
#
# class PdfxHandler(BaseModel):
#     job: UrlJob
#     content: bytes = bytes()
#     links: List[str] = []
#
#     def __download_pdf__(self):
#         """Download PDF file from URL"""
#         response = requests.get(self.job.url, timeout=self.job.timeout)
#         self.content = response.content
#
#     def __extract_links__(self) -> None:
#         """Extract all links from PDF file"""
#         if not self.content:
#             raise MissingInformationError()
#         with BytesIO(self.content) as pdf_file:
#             with PDFMinerBackend(pdf_file) as backend:
#                 refs = backend.get_references(reftype='A', sort=True)
#                 links = [ref[0] for ref in refs]
#         self.links = links
#
#     def download_and_extract(self):
#         self.__download_pdf__()
#         self.__extract_links__()
