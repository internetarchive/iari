from unittest import TestCase

from src.models.wikimedia.wikipedia.reference.extractor import (
    WikipediaReferenceExtractor,
)
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    easter_island_tail_excerpt,
    electrical_breakdown_full_article,
    old_norse_sources,
    test_full_article,
)

# wikibase = IASandboxWikibase()


class TestWikipediaReferenceExtractor(TestCase):
    def test_number_of_references_zero(self):
        wre0 = WikipediaReferenceExtractor(testing=True, wikitext="")
        wre0.extract_all_references()
        assert wre0.number_of_references == 0

    def test_number_of_references_two(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        raw_template2 = "{{citeq|Q2}}"
        raw_reference2 = f"<ref>{raw_template2}</ref>"
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=raw_reference + raw_reference2
        )
        # print(wre.wikitext)
        wre.extract_all_references()
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
            #
        )
        # print(wre1.wikitext)
        wre1.extract_all_references()
        assert wre1.number_of_references == 3

    # def test_extract_all_references(self):
    #     raw_template = "{{citeq|Q1}}"
    #     raw_reference = f"<ref>{raw_template}</ref>"
    #     wre2 = WikipediaReferenceExtractor(testing=True, wikitext=raw_reference)
    #     wre2.extract_all_references()
    #     assert wre2.number_of_references == 1
    #     assert wre2.references[0].first_parameter == "Q1"

    def test_extract_all_references_named_reference(self):
        raw_template = "{{citeq|Q1}}"
        named_reference = '<ref name="INE"/>'
        raw_reference = f"<ref>{raw_template}</ref>{named_reference}"
        wre2 = WikipediaReferenceExtractor(testing=True, wikitext=raw_reference)
        wre2.extract_all_references()
        assert wre2.number_of_references == 2
        assert wre2.number_of_content_references == 1
        assert wre2.number_of_empty_named_references == 1
        assert wre2.references[0].raw_reference.templates[0].name == "citeq"
        assert (
            wre2.references[0].raw_reference.templates[0].parameters["first_parameter"]
            == "Q1"
        )

    # def test_number_of_hashed_content_references(self):
    #     wre = WikipediaReferenceExtractor(
    #         testing=True, wikitext=easter_island_head_excerpt
    #     )
    #     wre.extract_all_references()
    #     assert wre.number_of_references == 3
    #     assert wre.number_of_content_references == 2
    #     assert wre.number_of_empty_named_references == 1
    #     assert wre.number_of_hashed_content_references == 2

    # def test_number_of_references_with_a_supported_template(self):
    #     wre = WikipediaReferenceExtractor(
    #         testing=True, wikitext=easter_island_head_excerpt
    #     )
    #     wre.extract_all_references()
    #     assert wre.number_of_content_references_with_any_supported_template == 2
    #
    # def test_number_of_cs1_references(self):
    #     wre = WikipediaReferenceExtractor(
    #         testing=True, wikitext=easter_island_head_excerpt
    #     )
    #     wre.extract_all_references()
    #     assert wre.number_of_cs1_references == 2

    def test___extract_all_raw_general_references__(self):
        """This tests extraction of sections and references"""
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt
        )
        wre.__extract_all_raw_general_references__()
        assert wre.number_of_sections_found == 3

    def test__extract_raw_templates_two(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        raw_template2 = "{{citeq|Q2}}"
        raw_reference2 = f"<ref>{raw_template2}</ref>"
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=raw_reference + raw_reference2
        )
        # print(wre.wikitext)
        wre.extract_all_references()
        assert wre.number_of_sections_found == 0
        assert wre.number_of_citation_references == 2
        assert wre.content_references[0].raw_reference.number_of_templates == 1
        assert wre.content_references[1].raw_reference.number_of_templates == 1

    def test__extract_sections_test(self):
        wre = WikipediaReferenceExtractor(testing=True, wikitext=test_full_article)
        wre.__extract_sections__()
        assert wre.number_of_sections_found == 0

    def test__extract_sections_easter_island(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt
        )
        wre.__extract_sections__()
        assert wre.number_of_sections_found == 3

    def test_extract_general_references_only(self):
        """This tests extraction of sections and references"""
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt
        )
        wre.extract_all_references()
        assert wre.number_of_sections_found == 3
        assert wre.number_of_general_references == 32
        # assert wre.number_of_content_reference_with_at_least_one_template == 22
        # assert wre.number_of_content_references_with_any_supported_template == 21
        # assert wre.number_of_cs1_references == 21
        # assert wre.number_of_citation_template_references == 0
        # assert wre.number_of_citeq_references == 0
        # assert wre.number_of_url_template_references == 0
        # assert wre.number_of_content_reference_without_a_template == 0
        assert wre.number_of_citation_references == 0
        # assert wre.number_of_hashed_content_references == 18

    def test_isbn_template(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="<ref>{{isbn|1234}}</ref>",
        )
        wre.extract_all_references()
        assert wre.number_of_content_references == 1
        assert wre.content_references[0].raw_reference.templates[0].name == "isbn"
        assert wre.content_references[0].raw_reference.templates[0].isbn == "1234"
        # assert wre.number_of_isbn_template_references == 1
        # assert wre.number_of_hashed_content_references == 1

    def test_first_level_domains_one(self):
        example_reference = "<ref>{{cite web|url=http://google.com}}</ref>"
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=example_reference, check_urls=True
        )
        wre.extract_all_references()
        assert wre.reference_first_level_domains == ["google.com"]

    def test_first_level_domains_two(self):
        example_reference = "<ref>{{cite web|url=http://google.com}}</ref>"
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext=example_reference + example_reference,
            check_urls=True,
        )
        wre.extract_all_references()
        assert wre.reference_first_level_domains == ["google.com", "google.com"]

    def test_first_level_domain_counts_simple(self):
        example_reference = "<ref>{{cite web|url=http://google.com}}</ref>"
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext=example_reference + example_reference,
            check_urls=True,
        )
        wre.extract_all_references()
        assert wre.reference_first_level_domain_counts == {"google.com": 2}

    # DISABLED because it takes to long
    # def test_first_level_domain_counts_excerpt(self):
    #     wre = WikipediaReferenceExtractor(
    #         testing=True,
    #         wikitext=easter_island_tail_excerpt,
    #         wikibase=wikibase,
    #     )
    #     wre.extract_all_references()
    #     assert len(wre.reference_first_level_domain_counts) == 7
    #     assert wre.reference_first_level_domain_counts == [
    #         {"archive.org": 4},
    #         {"google.com": 1},
    #         {"auckland.ac.nz": 1},
    #         {"usatoday.com": 1},
    #         {"oclc.org": 1},
    #         {"bnf.fr": 1},
    #         {"pisc.org.uk": 1},
    #     ]

    def test___get_checked_and_unique_reference_urls__(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="<ref>{{cite web|url=http://google.com}}</ref>",
            check_urls=True,
        )
        wre.extract_all_references()
        assert wre.number_of_references == 1
        assert len(wre.urls) == 1

    def test_reference_urls(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="<ref>{{cite web|url=http://google.com}}</ref>",
            check_urls=True,
        )
        wre.extract_all_references()
        assert len(wre.urls) == 1
        for url in wre.urls:
            assert url.url == "http://google.com"
            assert url.first_level_domain == "google.com"

    def test_has_references_true(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="<ref>{{isbn|1234}}</ref>",
        )
        wre.extract_all_references()
        assert wre.has_references is True

    def test_has_references_false(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="test",
        )
        wre.extract_all_references()
        assert wre.has_references is False

    # def test_malformed_urls_empty(self):
    #     wre = WikipediaReferenceExtractor(
    #         testing=True,
    #         wikitext="test",
    #     )
    #     wre.extract_all_references()
    #     assert wre.malformed_urls == []

    # def test_malformed_urls_one(self):
    #     wre = WikipediaReferenceExtractor(
    #         testing=True,
    #         wikitext="<ref>{{cite web|url=httpwww.google.com}}</ref>",
    #         check_urls=True,
    #     )
    #     wre.extract_all_references()
    #     assert wre.number_of_urls == 1
    #     # print(wre.urls)
    #     assert wre.malformed_urls == ["httpwww.google.com"]

    # def test_malformed_urls_two(self):
    #     """Test with two examples of malformed URLs"""
    #     wre = WikipediaReferenceExtractor(
    #         testing=True,
    #         wikitext="<ref>{{cite web|url=httpwww.google.com}}</ref><ref>{{cite web|url=google.com}}</ref>",
    #         check_urls=True,
    #     )
    #     wre.extract_all_references()
    #     assert wre.number_of_urls == 2
    #     # print(wre.urls)
    #     sorted_urls = sorted(wre.malformed_urls)
    #     assert sorted_urls == [
    #         "google.com",
    #         "httpwww.google.com",
    #     ]

    def test_sections_sources(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext=old_norse_sources,
            check_urls=False,
        )
        wre.extract_all_references()
        assert wre.number_of_sections_found == 1
        assert wre.number_of_general_references == 42

    def test_sections_no_general_references(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext=electrical_breakdown_full_article,
            check_urls=False,
        )
        wre.extract_all_references()
        assert wre.number_of_sections_found == 0
        assert wre.number_of_general_references == 0

    def test_sections_easter_island_tail(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext=easter_island_tail_excerpt,
        )
        wre.extract_all_references()
        assert wre.number_of_sections_found == 3
        assert wre.number_of_general_references == 32

    #
    # def test_combined_url_isbn_template_reference(self):
    #     wre = WikipediaReferenceExtractor(
    #         testing=True,
    #         wikitext="<ref>{{url|http://example.com}}{{isbn|1234}}</ref>",
    #         check_urls=False,
    #     )
    #     wre.extract_all_references()
    #     assert wre.number_of_isbn_template_references == 1
    #     assert wre.number_of_url_template_references == 1
