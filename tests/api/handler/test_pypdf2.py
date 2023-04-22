import unittest

from src.models.api.handlers.pypdf2 import PyPdf2Handler
from src.models.api.job.check_url_job import UrlJob


class TestPyPdf2Handler(unittest.TestCase):
    pdf_handler1 = PyPdf2Handler(
        job=UrlJob(
            url="https://www.campusdrugprevention.gov/sites/default/files/2021-11/Addressing-College-Drinking-and-Drug-Use%20(ACTA).pdf",
            timeout=10,
        )
    )
    pdf_handler2 = PyPdf2Handler(
        job=UrlJob(url="https://s1.q4cdn.com/806093406/files/doc_downloads/test.pdf")
    )

    def test_extract_links1(self):
        self.pdf_handler1.download_and_extract()
        assert len(self.pdf_handler1.links) == 79
        assert self.pdf_handler1.links[:10] == [
            "https://www.chronicle.com/resource/alcohol-s-influence-on-campus/6113/.",
            "https://www.samhsa.gov/data/sites/default/files/report_2361/ShortReport-2361.html.",
            "https://www.ncbi.nlm.nih.gov/pubmed/28728636.",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2701090/.",
            "http://archive.sph.harvard.edu/cas/Documents/",
            "https://nces.ed.gov/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3161136/;",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5280574/;",
            "https://www.ncbi.nlm.nih.gov/",
            "https://www.ncbi.nlm.nih.gov/pubmed/29680476.",
        ]

    def test_extract_links2(self):
        self.pdf_handler2.download_and_extract()
        assert self.pdf_handler2.links[:10] == []

    def test___fix_spaces__(self):
        string = "https://d oi.org/10.1186/s40779"
        pdf = PyPdf2Handler(job=UrlJob(url="test"))
        pdf.links = [string]
        pdf.__clean_spaces__()
        assert pdf.links[0] == "https://doi.org/10.1186/s40779"

    def test___discard_invalid_urls1(self):
        string = "https://www.science"
        pdf = PyPdf2Handler(job=UrlJob(url="test"))
        pdf.links = [string]
        pdf.__discard_invalid_urls__()
        assert pdf.links == []

    def test___discard_invalid_urls2(self):
        string = "https://patents.google.com/patent/CN210078382U/en?assignee=Wuhan+Institute+of+Virology+of+CAS&sort=new"
        pdf = PyPdf2Handler(job=UrlJob(url="test"))
        pdf.links = [string]
        pdf.__discard_invalid_urls__()
        assert pdf.links == [string]
