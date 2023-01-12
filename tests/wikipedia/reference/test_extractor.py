from unittest import TestCase

from src import IASandboxWikibase
from src.models.wikimedia.wikipedia.reference.extractor import (
    WikipediaReferenceExtractor,
)
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    easter_island_tail_excerpt,
    test_full_article,
)

wikibase = IASandboxWikibase()


class TestWikipediaReferenceExtractor(TestCase):
    def test_number_of_references_zero(self):
        wre0 = WikipediaReferenceExtractor(testing=True, wikitext="", wikibase=wikibase)
        wre0.extract_all_references()
        assert wre0.number_of_raw_references == 0
        assert wre0.number_of_references == 0

    def test_number_of_references_two(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        raw_template2 = "{{citeq|Q2}}"
        raw_reference2 = f"<ref>{raw_template2}</ref>"
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=raw_reference + raw_reference2, wikibase=wikibase
        )
        # print(wre.wikitext)
        wre.extract_all_references()
        assert wre.number_of_raw_references == 2
        assert wre.number_of_references == 2

    def test_number_of_references_three(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        raw_template2 = "{{cite web|url=http://google.com}}"
        raw_reference2 = f"<ref>{raw_template2}</ref>"
        raw_template3 = "{{citeq|Q3}}"
        raw_reference3 = f"<ref>{raw_template3}</ref>"
        wre1 = WikipediaReferenceExtractor(
            testing=True,
            wikitext=raw_reference + raw_reference2 + raw_reference3,
            wikibase=wikibase,
        )
        # print(wre1.wikitext)
        wre1.extract_all_references()
        assert wre1.number_of_raw_references == 3
        assert wre1.number_of_references == 3

    def test_extract_all_references(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wre2 = WikipediaReferenceExtractor(
            testing=True, wikitext=raw_reference, wikibase=wikibase
        )
        wre2.extract_all_references()
        assert wre2.number_of_references == 1
        assert wre2.references[0].first_template_name == "citeq"
        assert wre2.references[0].first_parameter == "Q1"

    def test_extract_all_references_named_reference(self):
        raw_template = "{{citeq|Q1}}"
        named_reference = '<ref name="INE"/>'
        raw_reference = f"<ref>{raw_template}</ref>{named_reference}"
        wre2 = WikipediaReferenceExtractor(
            testing=True, wikitext=raw_reference, wikibase=wikibase
        )
        wre2.extract_all_references()
        assert wre2.number_of_references == 2
        assert wre2.number_of_content_references == 1
        assert wre2.number_of_empty_named_references == 1
        assert wre2.references[0].first_template_name == "citeq"
        assert wre2.references[0].first_parameter == "Q1"

    def test_number_of_hashed_content_references(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_head_excerpt, wikibase=wikibase
        )
        wre.extract_all_references()
        assert wre.number_of_references == 3
        assert wre.number_of_content_references == 2
        assert wre.number_of_empty_named_references == 1
        assert wre.number_of_hashed_content_references == 2
        assert wre.percent_of_content_references_with_a_hash == 100

    def test_number_of_references_with_a_supported_template(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_head_excerpt, wikibase=wikibase
        )
        wre.extract_all_references()
        assert wre.number_of_content_references_with_any_supported_template == 2

    def test_number_of_cs1_references(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_head_excerpt, wikibase=wikibase
        )
        wre.extract_all_references()
        assert wre.number_of_cs1_references == 2

    def test___extract_all_raw_general_references__(self):
        """This tests extraction of sections and references"""
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt, wikibase=wikibase
        )
        wre.__extract_all_raw_general_references__()
        assert wre.number_of_sections_found == 2
        assert wre.number_of_raw_references == 22

    def test__extract_raw_templates_two(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        raw_template2 = "{{citeq|Q2}}"
        raw_reference2 = f"<ref>{raw_template2}</ref>"
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=raw_reference + raw_reference2, wikibase=wikibase
        )
        # print(wre.wikitext)
        wre.extract_all_references()
        assert wre.number_of_sections_found == 0
        assert wre.number_of_citation_references == 2
        assert wre.content_references[0].raw_reference.number_of_templates == 1
        assert wre.content_references[1].raw_reference.number_of_templates == 1

    def test__extract_sections_test(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=test_full_article, wikibase=wikibase
        )
        wre.__extract_sections__()
        assert wre.number_of_sections_found == 0

    def test__extract_sections_easter_island(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt, wikibase=wikibase
        )
        wre.__extract_sections__()
        assert wre.number_of_sections_found == 2

    def test_extract_general_references_only(self):
        """This tests extraction of sections and references"""
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt, wikibase=wikibase
        )
        wre.extract_all_references()
        assert wre.number_of_sections_found == 2
        assert wre.number_of_raw_references == 22
        assert wre.number_of_general_references == 22
        assert wre.number_of_content_reference_with_at_least_one_template == 22
        assert wre.number_of_content_references_with_any_supported_template == 21
        assert wre.number_of_cs1_references == 21
        assert wre.number_of_citation_template_references == 0
        assert wre.number_of_citeq_references == 0
        assert wre.number_of_url_template_references == 0
        assert wre.number_of_content_reference_without_a_template == 0
        assert wre.number_of_citation_references == 0
        assert wre.number_of_hashed_content_references == 18

    def test_percent_of_content_references_without_a_template_0(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt, wikibase=wikibase
        )
        wre.extract_all_references()
        assert wre.number_of_content_reference_without_a_template == 0
        assert wre.percent_of_content_references_without_a_template == 0

    def test_percent_of_content_references_without_a_template_100(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="<ref>test reference without a template</ref>",
            wikibase=wikibase,
        )
        wre.extract_all_references()
        assert wre.number_of_content_reference_without_a_template == 1
        assert wre.percent_of_content_references_without_a_template == 100

    def test_percent_of_content_references_with_a_hash_0(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="<ref>{{cite book|first=test|last=tester|title=test}}</ref>",
            wikibase=wikibase,
        )
        wre.extract_all_references()
        assert wre.number_of_content_references == 1
        assert wre.number_of_hashed_content_references == 0
        assert wre.percent_of_content_references_with_a_hash == 0

    def test_percent_of_content_references_with_a_hash_100(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="<ref>{{cite book|first=test|last=tester|title=test|isbn=1234}}</ref>",
            wikibase=wikibase,
        )
        wre.extract_all_references()
        assert wre.number_of_content_references == 1
        assert wre.number_of_hashed_content_references == 1
        assert wre.percent_of_content_references_with_a_hash == 100

    def test_isbn_template(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="<ref>{{isbn|1234}}</ref>",
            wikibase=wikibase,
        )
        wre.extract_all_references()
        assert wre.number_of_content_references == 1
        assert wre.number_of_isbn_template_references == 1
        assert wre.number_of_hashed_content_references == 1
        assert wre.percent_of_content_references_with_a_hash == 100
        assert wre.content_references[0].isbn == "1234"
