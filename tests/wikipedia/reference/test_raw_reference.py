from unittest import TestCase

from mwparserfromhell import parse  # type: ignore

from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.reference.raw_reference import WikipediaRawReference
from src.models.wikimedia.wikipedia.url import WikipediaUrl

# wikibase = IASandboxWikibase()


class TestWikipediaRawReference(TestCase):
    def test__extract_raw_templates_one(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            # print(ref)
            raw_reference_object = WikipediaRawReference(tag=ref)
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
            raw_reference_object = WikipediaRawReference(tag=ref)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.number_of_templates == 2
            assert raw_reference_object.multiple_templates_found is True

    def test___determine_reference_type_one_template(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.citeq_template_found is True
        raw_template = "{{cite q|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.citeq_template_found is True

    def test___determine_reference_type_cite_q_extra_params(self):
        url = "http://example.com"
        raw_template = f"{{{{citeq|Q1|url={url}}}}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref)
            raw_reference_object.extract_and_check()
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
            raw_reference_object = WikipediaRawReference(tag=ref)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.number_of_templates == 2
            assert raw_reference_object.multiple_templates_found is True

    def test_number_of_templates_one(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.number_of_templates == 1

    def test_number_of_templates_two(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template+raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref)
            raw_reference_object.__extract_templates_and_parameters__()
            assert raw_reference_object.number_of_templates == 2
            assert raw_reference_object.multiple_templates_found is True

    def test_get_wikipedia_reference_object_citeq(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, testing=True)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.number_of_templates == 1
            assert raw_reference_object.templates[0].name == "citeq"
            reference = raw_reference_object.get_finished_wikipedia_reference_object()
            assert raw_reference_object.number_of_templates == 1
            assert raw_reference_object.templates[0].raw_template == raw_template
            assert reference.raw_reference.templates[0].name == "citeq"
            assert reference.wikidata_qid == "Q1"

    def test_first_template_name(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, testing=True)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.number_of_templates == 1
            assert raw_reference_object.templates[0].name == "citeq"
            reference = raw_reference_object.get_finished_wikipedia_reference_object()
            assert raw_reference_object.number_of_templates == 1
            assert raw_reference_object.templates[0].raw_template == raw_template
            assert reference.raw_reference.templates[0].name == "citeq"

    def test_named_reference(self):
        ref = '<ref name="INE"/>'
        wikicode = parse(ref)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, testing=True)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.is_named_reference is True

    def test_get_wikicode_as_string(self):
        ref = '<ref name="INE"/>'
        wikicode = parse(ref)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaRawReference(tag=ref, testing=True)
            assert raw_reference_object.get_wikicode_as_string == ref

    def test_is_citation_reference(self):
        ref = "{{citeq|Q1}}"
        wikicode = parse(ref)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
            check_urls=False,
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
            is_general_reference=True,
            check_urls=False,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
            check_urls=False,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
            check_urls=False,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
            check_urls=False,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
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
            is_general_reference=True,
            check_urls=True,
        )
        raw_reference_object.extract_and_check()
        assert raw_reference_object.reference_urls == [
            WikipediaUrl(
                checked=True,
                error=False,
                first_level_domain="geocities.com",
                fld_is_ip=False,
                malformed_url=False,
                no_dns_record=True,
                status_code=0,
                url="https://www1.geocities.com/",
            )
        ]
        assert raw_reference_object.first_level_domains_done is True
        assert raw_reference_object.first_level_domains == ["geocities.com"]

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
            is_general_reference=True,
            check_urls=True,
        )
        raw_reference_object.extract_and_check()
        flds = sorted(raw_reference_object.first_level_domains)
        assert flds == [
            "archive.org",
            "geocities.com",
        ]

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
            is_general_reference=True,
            check_urls=False,
        )
        with self.assertRaises(MissingInformationError):
            raw_reference_object.__check_urls__()

    # def test___checked_urls_no_dns(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
    #         "|url=https://www1.geocities.com/}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaRawReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #         check_urls=True,
    #     )
    #     raw_reference_object.extract_and_check()
    #     urls = raw_reference_object.checked_urls
    #     assert raw_reference_object.check_urls_done is True
    #     assert urls[0].status_code == 0
    #     assert urls[0].checked is True
    #     assert urls[0].dns_record_found is False
    #
    # def test___checked_urls_200(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
    #         "|archive-url=http://web.archive.org}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaRawReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #         check_urls=True,
    #     )
    #     raw_reference_object.extract_and_check()
    #     urls = raw_reference_object.checked_urls
    #     assert raw_reference_object.check_urls_done is True
    #     assert raw_reference_object.first_level_domains == ["archive.org"]
    #     assert urls[0].first_level_domain == "archive.org"
    #     assert urls[0].status_code in [200, 0]
    #     assert urls[0].checked is True
    #     assert urls[0].dns_record_found is True

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
            is_general_reference=True,
            check_urls=False,
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
            is_general_reference=True,
        )
        raw_reference_object.__extract_external_wikicoded_links_from_the_reference__()
        assert raw_reference_object.wikicoded_links_done is True
        assert len(raw_reference_object.wikicoded_links) == 1
        assert raw_reference_object.wikicoded_links[0] == WikipediaUrl(
            url="http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour"
        )

    def test_multiple_cs1_templates(self):
        """This is a multitemplate reference of a special kind which we should detect
        It overcomplicates for us and should really be split into multiple <ref>
        references by the community if there is a consensus for that.

        The only way to detect it is to count if multiple cs1 templates
        are found in the same reference"""
        data = (
            '<ref name="territory">'
            "*{{Cite web|last=Benedikter|first=Thomas|date=19 June 2006|"
            "title=The working autonomies in Europe|"
            "url=http://www.gfbv.it/3dossier/eu-min/autonomy.html|publisher=[[Society for Threatened Peoples]]|"
            "quote=Denmark has established very specific territorial autonomies with its two island territories|"
            "access-date=8 June 2012|archive-date=9 March 2008|"
            "archive-url=https://web.archive.org/web/20080309063149/http://www.gfbv.it/3dossier/eu-min/autonomy."
            "html|url-status=dead}}"
            "*{{Cite web|last=Ackrén|first=Maria|date=November 2017|"
            "title=Greenland|url=http://www.world-autonomies.info/tas/Greenland/Pages/default.aspx|"
            "url-status=dead|archive-url=https://web.archive.org/web/20190830110832/http://www.world-"
            "autonomies.info/tas/Greenland/Pages/default.aspx|archive-date=30 August 2019|"
            "access-date=30 August 2019|publisher=Autonomy Arrangements in the World|quote=Faroese and "
            "Greenlandic are seen as official regional languages in the self-governing territories "
            "belonging to Denmark.}}"
            "*{{Cite web|date=3 June 2013|title=Greenland|"
            "url=https://ec.europa.eu/europeaid/countries/greenland_en|access-date=27 August 2019|"
            "website=International Cooperation and Development|publisher=[[European Commission]]|"
            "language=en|quote=Greenland [...] is an autonomous territory within the Kingdom of Denmark}}</ref>"
        )
        wikicode = parse(data)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode, testing=True, check_urls=False
        )
        raw_reference_object.extract_and_check()
        assert raw_reference_object.number_of_cs1_templates == 3
        assert raw_reference_object.multiple_cs1_templates_found is True

    def test_number_of_templates_missing_first_parameter_zero(self):
        data = (
            "<ref>{{url|1=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 <!--|alternate-full-text-url="
            "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 -->}}</ref>"
        )
        wikicode = parse(data)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode, testing=True, check_urls=False
        )
        raw_reference_object.extract_and_check()
        assert raw_reference_object.number_of_templates == 1
        assert raw_reference_object.number_of_templates_missing_first_parameter == 0

    def test_number_of_templates_missing_first_parameter_one(self):
        data = "<ref>{{url}}</ref>"
        wikicode = parse(data)
        raw_reference_object = WikipediaRawReference(
            wikicode=wikicode, testing=True, check_urls=False
        )
        raw_reference_object.extract_and_check()
        assert raw_reference_object.number_of_templates == 1
        print(raw_reference_object.templates[0].dict())
        assert raw_reference_object.number_of_templates_missing_first_parameter == 1
