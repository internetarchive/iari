from unittest import TestCase

from mwparserfromhell import parse  # type: ignore

from src import MissingInformationError
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.wikipedia.reference.raw_reference import WikipediaRawReference
from src.models.wikimedia.wikipedia.url import WikipediaUrl

wikibase = IASandboxWikibase()


class TestWikipediaRawReference(TestCase):
    def test__extract_raw_templates_one(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            # print(ref)
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
            raw_reference_object.extract_and_check_urls()
            assert raw_reference_object.number_of_templates == 2
            assert raw_reference_object.multiple_templates_found is True

    def test___determine_reference_type_one_template(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.extract_and_check_urls()
            assert raw_reference_object.citeq_template_found is True
        raw_template = "{{cite q|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.extract_and_check_urls()
            assert raw_reference_object.citeq_template_found is True

    def test___determine_reference_type_cite_q_extra_params(self):
        url = "http://example.com"
        raw_template = f"{{{{citeq|Q1|url={url}}}}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.extract_and_check_urls()
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
            raw_reference_object.extract_and_check_urls()
            assert raw_reference_object.number_of_templates == 2
            assert raw_reference_object.multiple_templates_found is True

    def test_number_of_templates_one(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, wikibase=wikibase)
            raw_reference_object.extract_and_check_urls()
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
            raw_reference_object.extract_and_check_urls()
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
            raw_reference_object.extract_and_check_urls()
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
            raw_reference_object.extract_and_check_urls()
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
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.is_general_reference is True
        assert raw_reference_object.cs1_template_found is True

    def test__plain_text_detected_before(self):
        wikitext = (
            "test{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.plain_text_in_reference is True

    def test__plain_text_detected_after(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong}}test"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.plain_text_in_reference is True

    def test__plain_text_detected_no(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.plain_text_in_reference is False

    def test_wayback_url_true(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=http://web.archive.org/web/19970222174751/https://www1.geocities.com/}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.web_archive_org_in_reference is True

    def test_wayback_url_false(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://www1.geocities.com/}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.web_archive_org_in_reference is False

    def test_archive_details_url_true(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://archive.org/details/delattre00herruoft}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.archive_org_slash_details_in_reference is True

    def test_archive_details_url_false(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://www1.geocities.com/}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.archive_org_slash_details_in_reference is False

    def test_google_books_url_true(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://books.google.se/books?id=9HRodACJLOoC&printsec="
            "frontcover&dq=test&hl=sv&sa=X&redir_esc=y#v=onepage&q=test&f=false}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.google_books_url_or_template_found is True

    def test_google_books_url_false(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://www1.geocities.com/}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.google_books_url_or_template_found is False

    def test_google_books_template_found_true(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url={{google books |plainurl=y |id=CDJpAAAAMAAJ |page=313}}}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.google_books_template_found is True

    def test_google_books_template_found_false(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://www1.geocities.com/}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.google_books_template_found is False

    def test_template_first_level_domains_one(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://www1.geocities.com/}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.first_level_domains == {"geocities.com"}

    def test_template_first_level_domains_two(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://www1.geocities.com/|archive-url=http://web.archive.org}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        assert raw_reference_object.first_level_domains == {
            "geocities.com",
            "archive.org",
        }

    def test___check_urls__missing_extraction(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://www1.geocities.com/|archive-url=http://web.archive.org}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        with self.assertRaises(MissingInformationError):
            raw_reference_object.__check_urls__()

    def test___checked_urls_no_dns(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://www1.geocities.com/}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        urls = raw_reference_object.checked_urls
        assert raw_reference_object.urls_checked is True
        assert urls[0].status_code == 0
        assert urls[0].checked is True
        assert urls[0].no_dns_record is True

    def test___checked_urls_200(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|archive-url=http://web.archive.org}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check_urls()
        urls = raw_reference_object.checked_urls
        assert raw_reference_object.urls_checked is True
        assert urls[0].status_code == 200
        assert urls[0].checked is True
        assert urls[0].no_dns_record is False

    def test___find_bare_urls__(self):
        """Test on a reference from the wild"""
        wikitext = (
            '<ref name="jew virt lib">[http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour'
            ' "IAF Aircraft Inventory: Sud-Ouest S.O. 4050 Vautour."] Jewish Virtual Library, '
            "Retrieved: 16 September 2017.</ref>"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        bare_urls = raw_reference_object.__find_bare_urls__()
        assert len(bare_urls) == 0

    def test___external_links_in_reference__(self):
        """Test on a reference from the wild"""
        wikitext = (
            '<ref name="jew virt lib">[http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour'
            ' "IAF Aircraft Inventory: Sud-Ouest S.O. 4050 Vautour."] Jewish Virtual Library, '
            "Retrieved: 16 September 2017.</ref>"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            wikibase=wikibase,
            is_general_reference=True,
        )
        assert (
            len(raw_reference_object.__external_wikicoded_links_in_the_reference__) == 1
        )
        assert raw_reference_object.__external_wikicoded_links_in_the_reference__[
            0
        ] == WikipediaUrl(
            url="http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour"
        )
