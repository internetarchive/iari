from unittest import TestCase

from mwparserfromhell import parse # type: ignore

from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.wikipedia.reference.raw_reference import WikipediaRawReference

wikibase = IASandboxWikibase()

class TestWikipediaRawReference(TestCase):
    def test__extract_raw_templates__(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.__extract_raw_templates__()
            assert raw_reference_object.templates[0].raw_template == raw_template

    def test___determine_reference_type__(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.__extract_templates_and_parameters_from_raw_reference__()
            raw_reference_object.__determine_reference_type__()
            assert raw_reference_object.citeq_template_found is True

    def test_number_of_templates(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.__extract_templates_and_parameters_from_raw_reference__()
            assert raw_reference_object.number_of_templates == 1

    def test_get_wikipedia_reference_object(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, testing=True, wikibase=wikibase)
            reference = raw_reference_object.extract_determine_type_and_get_finished_wikipedia_reference_object()
            assert reference.template_name == "citeq"
            assert reference.wikidata_qid == "Q1"
