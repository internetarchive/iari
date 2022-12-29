from unittest import TestCase

from src import IASandboxWikibase
from src.models.wikimedia.wikipedia.reference.extractor import (
    WikipediaReferenceExtractor,
)

wikibase = IASandboxWikibase()


class TestWikipediaReferenceExtractor(TestCase):
    def test_number_of_references_two(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        raw_template2 = "{{citeq|Q2}}"
        raw_reference2 = f"<ref>{raw_template2}</ref>"
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=raw_reference + raw_reference2, wikibase=wikibase
        )
        #print(wre.wikitext)
        wre.extract_all_references()
        assert wre.number_of_references == 2
        raw_template2 = "{{cite web|url=http://google.com}}"
        raw_reference2 = f"<ref>{raw_template2}</ref>"
        raw_template3 = "{{citeq|Q3}}"
        raw_reference3 = f"<ref>{raw_template3}</ref>"
        wre1 = WikipediaReferenceExtractor(
            testing=True,
            wikitext=raw_reference + raw_reference2 + raw_reference3,
            wikibase=wikibase,
        )
        #print(wre1.wikitext)
        wre1.extract_all_references()
        assert wre1.number_of_references == 3

    def test_extract_all_references(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wre2 = WikipediaReferenceExtractor(
            testing=True, wikitext=raw_reference, wikibase=wikibase
        )
        wre2.extract_all_references()
        assert wre2.number_of_references == 1
        assert wre2.references[0].template_name == "citeq"
        assert wre2.references[0].first_parameter == "Q1"
