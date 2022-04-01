from unittest import TestCase

from src import console
from src.models.wikimedia.wikipedia.templates.english_wikipedia_page_reference import (
    EnglishWikipediaPageReferenceSchema,
    EnglishWikipediaPageReference,
)


class TestEnglishWikipediaPageReferenceSchema(TestCase):
    def test_url_template1(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
        }

        reference = EnglishWikipediaPageReferenceSchema().load(data)
        console.print(reference)

    def test_url_template2(self):
        data = {"1": "chkchkchk.net", "template_name": "url"}
        reference = EnglishWikipediaPageReferenceSchema().load(data)
        console.print(reference)

    def test_parse_persons_from_cite_web(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
        }

        reference: EnglishWikipediaPageReference = (
            EnglishWikipediaPageReferenceSchema().load(data)
        )
        reference.parse_persons()
        console.print(reference)
        person = reference.persons_without_role[0]
        assert person.given == "Melissa"
        assert person.surname == "Locker"

    def test_parse_persons_from_cite_journal(self):
        data = {
            "last1": "Skaaning",
            "first1": "Svend-Erik",
            "title": "Different Types of Data and the Validity of Democracy Measures",
            "journal": "Politics and Governance",
            "volume": "6",
            "issue": "1",
            "page": "105",
            "doi": "10.17645/pag.v6i1.1183",
            "year": "2018",
            "doi_access": "free",
            "template_name": "cite journal",
        }
        reference: EnglishWikipediaPageReference = (
            EnglishWikipediaPageReferenceSchema().load(data)
        )
        reference.parse_persons()
        console.print(reference)
        person = reference.persons_without_role[0]
        assert person.given == "Svend-Erik"
        assert person.surname == "Skaaning"
