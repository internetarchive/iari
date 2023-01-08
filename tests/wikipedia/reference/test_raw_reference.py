from unittest import TestCase

from mwparserfromhell import parse  # type: ignore

from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.wikipedia.reference.raw_reference import WikipediaRawReference

wikibase = IASandboxWikibase()


class TestWikipediaRawReference(TestCase):
    def test__extract_raw_templates_one(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            print(ref)
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.__extract_raw_templates__()
            assert raw_reference_object.number_of_templates == 1
            assert raw_reference_object.templates[0].raw_template == raw_template

    def test_extract_raw_templates_multiple_templates(self):
        raw_template1 = "{{citeq|Q1}}"
        raw_template2 = "{{citeq|Q2}}"
        raw_reference = f"<ref>{raw_template1+raw_template2}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.extract_and_determine_reference_type()
            assert raw_reference_object.number_of_templates == 2
            assert raw_reference_object.multiple_templates_found is True

    def test___determine_reference_type_one_template(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.extract_and_determine_reference_type()
            assert raw_reference_object.citeq_template_found is True
        raw_template = "{{cite q|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.extract_and_determine_reference_type()
            assert raw_reference_object.citeq_template_found is True

    def test___determine_reference_type_cite_q_extra_params(self):
        url = "http://example.com"
        raw_template = f"{{{{citeq|Q1|url={url}}}}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.extract_and_determine_reference_type()
            assert raw_reference_object.citeq_template_found is True
            assert (
                raw_reference_object.templates[0].parameters["first_parameter"] == "Q1"
            )
            assert raw_reference_object.templates[0].parameters["url"] == url

    def test___determine_reference_type_two_templates(self):
        raw_template1 = "{{citeq|Q1}}"
        raw_template2 = "{{citeq|Q2}}"
        raw_reference = f"<ref>{raw_template1+raw_template2}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.extract_and_determine_reference_type()
            assert raw_reference_object.number_of_templates == 2
            assert raw_reference_object.multiple_templates_found is True

    def test_number_of_templates_one(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.extract_and_determine_reference_type()
            assert raw_reference_object.number_of_templates == 1

    def test_number_of_templates_two(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template+raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.__extract_templates_and_parameters_from_raw_reference__()
            assert raw_reference_object.number_of_templates == 2
            assert raw_reference_object.multiple_templates_found is True

    def test_get_wikipedia_reference_object_citeq(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(
                tag=ref, testing=True, wikibase=wikibase
            )
            raw_reference_object.extract_and_determine_reference_type()
            assert raw_reference_object.number_of_templates == 1
            assert raw_reference_object.templates[0].name == "citeq"
            assert raw_reference_object.first_template_name == "citeq"
            reference = raw_reference_object.get_finished_wikipedia_reference_object()
            assert raw_reference_object.number_of_templates == 1
            assert raw_reference_object.templates[0].raw_template == raw_template
            assert reference.first_template_name == "citeq"
            assert reference.first_parameter == "Q1"
            assert reference.wikidata_qid == "Q1"

    def test_first_template_name(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(
                tag=ref, testing=True, wikibase=wikibase
            )
            raw_reference_object.extract_and_determine_reference_type()
            assert raw_reference_object.number_of_templates == 1
            assert raw_reference_object.templates[0].name == "citeq"
            assert raw_reference_object.first_template_name == "citeq"
            reference = raw_reference_object.get_finished_wikipedia_reference_object()
            assert raw_reference_object.number_of_templates == 1
            assert raw_reference_object.templates[0].raw_template == raw_template
            assert reference.first_template_name == "citeq"

    def test_named_reference(self):
        ref = '<ref name="INE"/>'
        wikicode = parse(ref)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(
                tag=ref, testing=True, wikibase=wikibase
            )
            raw_reference_object.extract_and_determine_reference_type()
            assert raw_reference_object.is_named_reference is True

    def test_get_wikicode_as_string(self):
        ref = '<ref name="INE"/>'
        wikicode = parse(ref)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(
                tag=ref, testing=True, wikibase=wikibase
            )
            assert raw_reference_object.get_wikicode_as_string == ref

    def test_is_citation_reference(self):
        ref = "{{citeq|Q1}}"
        wikicode = parse(ref)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        assert raw_reference_object.is_citation_reference is False
        assert raw_reference_object.is_general_reference is True

    def test_is_cs1_reference(self):
        wikitext = (
            "* {{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_determine_reference_type()
        assert raw_reference_object.is_general_reference is True
        assert raw_reference_object.cs1_template_found is True
