# import unittest
#
# from src.models.api.handlers.pdfx import PdfxHandler
# from src.models.api.job.check_url_job import UrlJob
#
#
# class TestPdfxHandler(unittest.TestCase):
#
#     def setUp(self):
#         url_job1 = UrlJob(url='https://s3.documentcloud.org/documents/23782225/mwg-fdr-document-04-16-23-1.pdf', timeout=10)
#         self.pdf_handler1 = PdfxHandler(job=url_job1)
#         self.pdf_handler1.__download_pdf__()
#         url_job2 = UrlJob(url="https://s1.q4cdn.com/806093406/files/doc_downloads/test.pdf")
#         self.pdf_handler2 = PdfxHandler(job=url_job2)
#         self.pdf_handler2.__download_pdf__()
#
#     def test_download_pdf1(self):
#         result = self.pdf_handler1.content
#         self.assertIsNotNone(result)
#         self.assertTrue(isinstance(result, bytes))
#
#     def test_download_pdf2(self):
#         result = self.pdf_handler2.content
#         self.assertIsNotNone(result)
#         self.assertTrue(isinstance(result, bytes))
#
#     def test_extract_links1(self):
#         self.pdf_handler1.__extract_links__()
#         expected_links = [
#             'http://www.army.mil/',
#             'http://www.af.mil/',
#             'http://www.navy.mil/',
#             'http://www.marines.mil/',
#             'http://www.uscg.mil/',
#             'https://www.govinfo.gov/content/pkg/CHRG-117hhrg42552/pdf/CHRG-117hhrg42552.pdf'
#         ]
#         self.assertEqual(self.pdf_handler1.links, expected_links)
#
#     def test_extract_links2(self):
#         self.pdf_handler2.__extract_links__()
#         expected_links = [
#             'http://www.army.mil/',
#             'http://www.af.mil/',
#             'http://www.navy.mil/',
#             'http://www.marines.mil/',
#             'http://www.uscg.mil/',
#             'https://www.govinfo.gov/content/pkg/CHRG-117hhrg42552/pdf/CHRG-117hhrg42552.pdf'
#         ]
#         self.assertEqual(self.pdf_handler1.links, expected_links)
