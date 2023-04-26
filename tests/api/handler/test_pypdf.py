import unittest

from src.models.api.handlers.pypdf import PypdfHandler
from src.models.api.job.check_url_job import UrlJob


class TestPypdfHandler(unittest.TestCase):
    pdf_handler1 = PypdfHandler(
        job=UrlJob(
            url="https://www.campusdrugprevention.gov/sites/default/files/2021-11/Addressing-College-Drinking-and-Drug-Use%20(ACTA).pdf",
            timeout=10,
        )
    )
    pdf_handler2 = PypdfHandler(
        job=UrlJob(url="https://s1.q4cdn.com/806093406/files/doc_downloads/test.pdf")
    )
    pdf_handler3 = PypdfHandler(
        job=UrlJob(
            url="https://www.foundationforfreedomonline.com/wp-content/uploads/2023/03/FFO-FLASH-REPORT-REV.pdf"
        )
    )

    def test_extract_links1(self):
        self.pdf_handler1.download_and_extract()
        assert self.pdf_handler1.total_number_of_links == 79

    def test_extract_links2(self):
        self.pdf_handler2.download_and_extract()
        assert self.pdf_handler2.total_number_of_links == 0

    def test___fix_spaces__(self):
        string = "https://d oi.org/10.1186/s40779"
        correct = "https://doi.org/10.1186/s40779"
        pdf = PypdfHandler(job=UrlJob(url="test"))
        assert pdf.__clean_urls__(urls=[string]) == [correct]

    def test___discard_invalid_urls1(self):
        string = "https://www.science"
        pdf = PypdfHandler(job=UrlJob(url="test"))
        assert pdf.__discard_invalid_urls__(urls=[string]) == []

    def test___discard_invalid_urls2(self):
        string = "https://patents.google.com/patent/CN210078382U/en?assignee=Wuhan+Institute+of+Virology+of+CAS&sort=new"
        pdf = PypdfHandler(job=UrlJob(url="test"))
        assert pdf.__discard_invalid_urls__(urls=[string]) == [string]

    def test_linebreak_url_extraction(self):
        pdf = self.pdf_handler3
        pdf.download_and_extract()
        for page in pdf.pages:
            print(page)

    def test_get_dict1(self):
        self.pdf_handler1.download_and_extract()
        data = self.pdf_handler1.get_dict()
        assert "links_total" in data
        assert data["links_total"] == 79
        assert "links" in data
        assert len(data["links"]) == 40
        assert data["links"][30] == [
            "https://www.chronicle.com/resource/alcohol-s-influence-on-campus/6113/."
        ]
        assert "pages" in data
        assert len(data["pages"]) == 40
        assert data["pages"][30] == (
            "27\n"
            "A Primer for T rustees, Administrators, and Alumniother harmful substances "
            "on individual campuses. And collaborating with other \n"
            "institutions will magnify the impact. University leaders must share "
            "effective strategies \n"
            "that have worked for their respective institutions and consider broader "
            "policies at the \n"
            "local and state levels. Statewide initiatives can help solve states’ "
            "long-term problems, \n"
            "and these initiatives can also garner state funding. \n"
            "Together, college leadership can help to impress upon students from every "
            "region that \n"
            "they must not allow substance use to interfere with the precious opportunity "
            "that \n"
            "college students have to learn and grow.  \n"
            "n    n     n\n"
            "RECOMMENDED\tREADING\n"
            "Alcohol’s Influence on Campus . Chronicle  Focus Collection. Washington, DC: "
            "The Chronicle of Higher Education , 2016. \n"
            "https://www.chronicle.com/resource/alcohol-s-influence-on-campus/6113/.\n"
            "Berenson, Alex. T ell Your Children: The Truth about Marijuana, Mental "
            "Illness, and Violence . New York: Free Press, 2019. \n"
            "Cimini, M. Dolores and Estela M. Rivero (Eds.). Promoting Behavioral Health "
            "and Reducing Risk Among College Students: \n"
            "A Comprehensive Approach . United Kingdom: Routledge, 2018. \n"
            "DuPont, Robert L. Chemical Slavery: Understanding Addiction and Stopping the "
            "Drug Epidemic . Rockville, MD: Institute \n"
            "for Behavior and Health, 2018.   "
        )
