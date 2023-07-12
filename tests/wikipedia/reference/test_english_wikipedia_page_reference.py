import logging
from collections import OrderedDict
from unittest import TestCase

from mwparserfromhell import parse  # type: ignore

import config
from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference
from src.models.wikimedia.wikipedia.url import WikipediaUrl

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


# wikibase = IASandboxWikibase()


class TestEnglishWikipediaReferenceSchema(TestCase):
    pass

    # def test_url_template1(self):
    #     data = {
    #         "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
    #         "title": "Turntable Interview: !!!",
    #         "last": "Locker",
    #         "first": "Melissa",
    #         "date": "May 9, 2013",
    #         "website": "Stereogum",
    #         "access_date": "May 24, 2021",
    #         "template_name": "cite web",
    #     }
    #
    #     reference = EnglishWikipediaReferenceSchema().load(data)
    #     # console.print(reference)
    #     assert (
    #         reference.url
    #         == "https://www.stereogum.com/1345401/turntable-interview/interviews/"
    #     )
    #
    # def test_url_template_with_archive_url(self):
    #     data = {
    #         "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
    #         "title": "Turntable Interview: !!!",
    #         "last": "Locker",
    #         "first": "Melissa",
    #         "date": "May 9, 2013",
    #         "website": "Stereogum",
    #         "access_date": "May 24, 2021",
    #         "template_name": "cite web",
    #         "archive_url": "https://web.archive.org/web/20100715195638/"
    #         "http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
    #     }
    #
    #     reference = EnglishWikipediaReferenceSchema().load(data)
    #     assert (
    #         reference.url
    #         == "https://www.stereogum.com/1345401/turntable-interview/interviews/"
    #     )
    #     assert (
    #         reference.archive_url
    #         == "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/"
    #         "chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php"
    #     )
    #     # console.print(reference)

    # def test_parse_persons_from_cite_web(self):
    #     data = {
    #         "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
    #         "title": "Turntable Interview: !!!",
    #         "last": "Locker",
    #         "first": "Melissa",
    #         "date": "May 9, 2013",
    #         "website": "Stereogum",
    #         "access_date": "May 24, 2021",
    #         "template_name": "cite web",
    #     }
    #
    #     reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
    #         data
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     # console.print(reference)
    #     person = reference.persons_without_role[0]
    #     assert person.given == "Melissa"
    #     assert person.surname == "Locker"

    # def test_parse_persons_from_cite_journal(self):
    #     data = {
    #         "last1": "Skaaning",
    #         "first1": "Svend-Erik",
    #         "title": "Different Types of Data and the Validity of Democracy Measures",
    #         "journal": "Politics and Governance",
    #         "volume": "6",
    #         "issue": "1",
    #         "page": "105",
    #         "doi": "10.17645/pag.v6i1.1183",
    #         "year": "2018",
    #         "doi_access": "free",
    #         "template_name": "cite journal",
    #     }
    #     reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
    #         data
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     console.print(reference)
    #     person = reference.persons_without_role[0]
    #     assert person.given == "Svend-Erik"
    #     assert person.surname == "Skaaning"
    #
    # def test_parse_persons_from_cite_book(self):
    #     data = {
    #         "last": "Tangian",
    #         "first": "Andranik",
    #         "date": "2020",
    #         "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
    #         "series": "Studies in Choice and Welfare",
    #         "publisher": "Springer",
    #         "location": "Cham, Switzerland",
    #         "isbn": "978-3-030-39690-9",
    #         "doi": "10.1007/978-3-030-39691-6",
    #         "s2cid": "216190330",
    #         "template_name": "cite book",
    #     }
    #     reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
    #         data
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     console.print(reference)
    #     person = reference.persons_without_role[0]
    #     assert person.given == "Andranik"
    #     assert person.surname == "Tangian"

    # def test_extract_first_level_domain(self):
    #     data = {
    #         "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
    #         "title": "Turntable Interview: !!!",
    #         "last": "Locker",
    #         "first": "Melissa",
    #         "date": "May 9, 2013",
    #         "website": "Stereogum",
    #         "access_date": "May 24, 2021",
    #         "template_name": "cite web",
    #         "archive_url": "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/"
    #         "chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
    #     }
    #     reference = EnglishWikipediaReferenceSchema().load(data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.first_level_domain_of_url == "stereogum.com"
    #     assert (
    #         reference.url
    #         == "https://www.stereogum.com/1345401/turntable-interview/interviews/"
    #     )

    # TODO move this to TestTemplate once parsing of urls has been implemented there
    # def test_extract_first_level_domain_bad_url(self):
    #     data = {
    #         "url": "[[:sq:Shkrime për historinë e Shqipërisë|Shkrime për historinë e Shqipërisë]]",
    #         "title": "Turntable Interview: !!!",
    #         "last": "Locker",
    #         "first": "Melissa",
    #         "date": "May 9, 2013",
    #         "website": "Stereogum",
    #         "access_date": "May 24, 2021",
    #         "template_name": "cite web",
    #         "archive_url": "https://web.archive.org/web/20100715195638/http://
    #         www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
    #     }
    #     reference = EnglishWikipediaReferenceSchema().load(data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.url == ""

    # def test_extract_first_level_domain_google_books_template(self):
    #     data = {
    #         "url": "{{Google books|plainurl=yes|id=MdPDAQAAQBAJ|page=25}}",
    #         "title": "Turntable Interview: !!!",
    #         "last": "Locker",
    #         "first": "Melissa",
    #         "date": "May 9, 2013",
    #         "website": "Stereogum",
    #         "access_date": "May 24, 2021",
    #         "template_name": "cite web",
    #         "archive_url":
    #         "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
    #     }
    #     reference = EnglishWikipediaReferenceSchema().load(data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.url == ""

    # def test_find_number(self):
    #     ref = EnglishWikipediaReference(
    #         template_name="test",
    #         wikibase=IASandboxWikibase(),
    #     )
    #     with self.assertRaises(MoreThanOneNumberError):
    #         ref.__find_number__(string="123one123")
    #     assert ref.__find_number__(string="1one") == 1
    #     assert ref.__find_number__(string="one1one") == 1
    #     assert ref.__find_number__(string="one") is None
    #
    # def test_publisher_and_location(self):
    #     data = dict(
    #         template_name="cite web",
    #         url="http://www.kmk.a.se/ImageUpload/kmkNytt0110.pdf",
    #         archive_url="https://web.archive.org/web/20100812051822/http://www.kmk.a.se/ImageUpload/kmkNytt0110.pdf",
    #         url_status="dead",
    #         archive_date="2010-08-12",
    #         title="Musköbasen 40 år",
    #         first="Helene",
    #         last="Skoglund",
    #         author2="Nynäshamns Posten",
    #         date="January 2010",
    #         publisher="Kungliga Motorbåt Klubben",
    #         location="Stockholm",
    #         pages="4–7",
    #         language="Swedish",
    #         trans_title="Muskö Naval Base 40 years",
    #         access_date="2010-11-09",
    #     )
    #     reference = EnglishWikipediaReferenceSchema().load(data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.publisher == "Kungliga Motorbåt Klubben"
    #     assert reference.location == "Stockholm"

    # def test_detect_archive_urls(self):
    #     # test other archives also
    #     from src.models.wikibase.enums import KnownArchiveUrl
    #
    #     reference = EnglishWikipediaReference(
    #         wikibase=IASandboxWikibase(),
    #         archive_url="https://web.archive.org/web/20190701062212/http://www.mgtrust.org/ind1.htm",
    #         template_name="test",
    #     )
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     # logger.debug(reference.detected_archive_of_url)
    #     # logger.debug(reference.detected_archive_of_archive_url)
    #     assert reference.detected_archive_of_url is None
    #     assert reference.detected_archive_of_archive_url == KnownArchiveUrl.ARCHIVE_ORG

    # DEPRECATED since 2.1.0-alpha3
    # def test_google_books(self):
    #     data = {
    #         "url": "{{google books |plainurl=y |id=CDJpAAAAMAAJ |page=313}}",
    #         "title": "Turntable Interview: !!!",
    #         "last": "Locker",
    #         "first": "Melissa",
    #         "date": "May 9, 2013",
    #         "website": "Stereogum",
    #         "access_date": "May 24, 2021",
    #         "template_name": "cite web",
    #     }
    #     reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
    #         data
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     # console.print(type(reference.google_books))
    #     assert reference.first_level_domain_of_url == "google.com"
    #     self.assertIsInstance(reference.google_books, GoogleBooks)

    # def test_detect_internet_archive_id(self):
    #     data = dict(
    #         url="https://archive.org/details/catalogueofshipw0000wils/",
    #         template_name="cite book",
    #     )
    #     reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
    #         data
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     # print(reference.internet_archive_id)
    #     assert reference.internet_archive_id == "catalogueofshipw0000wils"

    # DEPRECATED since 2.1.0-alpha3
    # def test_detect_google_books_id(self):
    #     data = dict(
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
    #         data
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     # print(reference.internet_archive_id)
    #     assert reference.google_books_id == "on0TaPqFXbcC"

    # def test_clean_wiki_markup_from_strings(self):
    #     data = dict(
    #         publisher="[[test]]",
    #         template_name="cite book",
    #     )
    #     reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
    #         data
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     # print(reference.internet_archive_id)
    #     assert reference.publisher == "test"
    #     data = dict(
    #         # publisher="",
    #         template_name="cite book",
    #     )
    #     reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
    #         data
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     # print(reference.internet_archive_id)
    #     assert reference.publisher is None

    # def test_clean_wiki_markup_from_strings_complicated_markup(self):
    #     data = dict(
    #         publisher="[[test|test2]]",
    #         template_name="cite book",
    #     )
    #     reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
    #         data
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.publisher == "test"

    # def test_handle_place(self):
    #     data = dict(
    #         place="Copenhagen",
    #         template_name="cite book",
    #     )
    #     reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
    #         data
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.location == "Copenhagen"
    #
    # def test_handle_lang(self):
    #     data = dict(
    #         lang="English",
    #         template_name="cite book",
    #     )
    #     reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
    #         data
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.language == "English"
    #
    # def test_periodical(self):
    #     data = dict(
    #         template_name="cite web",
    #         periodical="test",
    #     )
    #     reference = EnglishWikipediaReferenceSchema().load(data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.periodical == "test"
    #
    # def test_oclc(self):
    #     data = dict(
    #         oclc="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.oclc == "test"

    # Disabled because we don't generate tld fld hash right now
    # def test_has_first_level_domain_url_hash_and_has_hash(self):
    #     data = dict(
    #         oclc="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     assert reference.has_first_level_domain_url_hash is False
    #     assert reference.has_hash is False
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.has_first_level_domain_url_hash is True
    #     assert reference.has_hash is True

    # def test_template_url(self):
    #     raw_template = "{{citeq|Q1}}"
    #     raw_reference = f"<ref>{raw_template}</ref>"
    #     wikicode = parse(raw_reference)
    #     refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
    #     for ref in refs:
    #         raw_reference_object = WikipediaReference(
    #             wikicode=ref, testing=True, wikibase=wikibase
    #         )
    #         raw_reference_object.extract_and_determine_reference_type()
    #         assert raw_reference_object.number_of_templates == 1
    #         assert raw_reference_object.templates[0].name == "citeq"
    #         assert raw_reference_object.first_template_name == "citeq"
    #         reference = raw_reference_object.get_finished_wikipedia_reference_object()
    #         assert (
    #             reference.template_url
    #             == f"https://en.wikipedia.org/wiki/Template:citeq"
    #         )

    # def test_wikibase_url(self):
    #     data = dict(
    #         oclc="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     with self.assertRaises(MissingInformationError):
    #         print(reference.wikibase_url)
    #     reference.return_ = WikibaseReturn(item_qid="test", uploaded_now=False)
    #     # print(reference.wikibase_url)
    #     assert (
    #         reference.wikibase_url
    #         == f"https://ia-sandbox.wikibase.cloud/wiki/Item:test"
    #     )

    # DEPRECATED since 2.1.0-alpha3
    # def test_google_books_template_in_chapter_url(self):
    #     """Test for https://github.com/internetarchive/wcdimportbot/issues/148"""
    #     data = dict(
    #         oclc="test",
    #         chapter_url="{{Google books|plainurl=yes|id=MdPDAQAAQBAJ|page=25}}",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.chapter_url == "https://books.google.com/books?id=MdPDAQAAQBAJ"

    # TODO enable this when we support nested templates
    # def test_google_books_template_handling(self):
    #     data = dict(
    #         oclc="test",
    #         url="{{Google books|plainurl=yes|id=MdPDAQAAQBAJ|page=25}}",
    #         chapter_url="{{Google books|plainurl=yes|id=MdPDAQAAQBAJ|page=25}}",
    #         lay_url="{{Google books|plainurl=yes|id=MdPDAQAAQBAJ|page=25}}",
    #         transcripturl="{{Google books|plainurl=yes|id=MdPDAQAAQBAJ|page=25}}",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.url == "https://books.google.com/books?id=MdPDAQAAQBAJ"
    #     assert reference.chapter_url == "https://books.google.com/books?id=MdPDAQAAQBAJ"
    #     assert reference.lay_url == "https://books.google.com/books?id=MdPDAQAAQBAJ"
    #     assert (
    #         reference.transcripturl == "https://books.google.com/books?id=MdPDAQAAQBAJ"
    #     )

    # def test_parse_url(self):
    #     reference = EnglishWikipediaReference(template_name="")
    #     assert (
    #         reference.__parse_url__(
    #             url="{{Google books|plainurl=yes|id=MdPDAQAAQBAJ|page=25}}"
    #         )
    #         == "https://books.google.com/books?id=MdPDAQAAQBAJ"
    #     )
    #     assert (
    #         reference.__parse_url__(
    #             url="[[:sq:Shkrime për historinë e Shqipërisë|Shkrime për historinë e Shqipërisë]]"
    #         )
    #         == ""
    #     )

    # TODO update to changes in model
    # def test__get_url_from_template__(self):
    #     reference = EnglishWikipediaReference(template_name="")
    #     assert (
    #         reference.__get_url_from_template__(
    #             url="{{Google books|plainurl=yes|id=MdPDAQAAQBAJ|page=25}}"
    #         )
    #         == "https://books.google.com/books?id=MdPDAQAAQBAJ"
    #     )
    #
    # def test__get_url_from_google_books_template__(self):
    #     reference = EnglishWikipediaReference(template_name="")
    #     assert (
    #         reference.__get_url_from_google_books_template__(
    #             url="{{Google books|plainurl=yes|id=MdPDAQAAQBAJ|page=25}}"
    #         )
    #         == "https://books.google.com/books?id=MdPDAQAAQBAJ"
    #     )

    # def test_parse_first_parameter_citeq(self):
    #     raw_template = "{{citeq|Q1}}"
    #     raw_reference = f"<ref>{raw_template}</ref>"
    #     wikicode = parse(raw_reference)
    #     refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
    #     for ref in refs:
    #         raw_reference_object = WikipediaReference(
    #             wikicode=ref,
    #             # wikibase=wikibase
    #         )
    #         reference = raw_reference_object.get_finished_wikipedia_reference_object()
    #         reference.finish_parsing_and_generate_hash()
    #         assert reference.first_parameter == "Q1"
    #         assert reference.wikidata_qid == "Q1"

    # def test_parse_first_parameter_cite_q(self):
    #     raw_template1 = "{{cite q|Q1}}"
    #     raw_reference1 = f"<ref>{raw_template1}</ref>"
    #     wikicode = parse(raw_reference1)
    #     refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
    #     for ref in refs:
    #         raw_reference_object = WikipediaReference(
    #             wikicode=ref,
    #             # wikibase=wikibase
    #         )
    #         reference = raw_reference_object.get_finished_wikipedia_reference_object()
    #         reference.finish_parsing_and_generate_hash()
    #         assert reference.first_parameter == "Q1"
    #         assert reference.wikidata_qid == "Q1"

    # def test_generate_reference_hash_based_on_wikidata_qid(self):
    #     data = dict(
    #         wikidata_qid="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.has_hash is True
    #     assert reference.md5hash == "7f48f6452d26e9b56cc5039dffbe6ecd"

    # def test_generate_reference_hash_based_on_doi(self):
    #     data = dict(
    #         doi="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.has_hash is True
    #     assert reference.md5hash == "7f48f6452d26e9b56cc5039dffbe6ecd"

    # def test_generate_reference_hash_based_on_pmid(self):
    #     data = dict(
    #         pmid="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.has_hash is True
    #     assert reference.md5hash == "7f48f6452d26e9b56cc5039dffbe6ecd"

    # def test_generate_reference_hash_based_on_isbn(self):
    #     data = dict(
    #         isbn="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.has_hash is True
    #     assert reference.md5hash == "7f48f6452d26e9b56cc5039dffbe6ecd"

    # def test_generate_reference_hash_based_on_oclc(self):
    #     data = dict(
    #         oclc="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.has_hash is True
    #     assert reference.md5hash == "7f48f6452d26e9b56cc5039dffbe6ecd"
    #
    # def test_generate_reference_hash_based_on_url(self):
    #     data = dict(
    #         # oclc="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.has_hash is True
    #     assert reference.md5hash == "9fe13e5007b27e99897000a584bf631d"
    #
    # def test_has_hash_empty(self):
    #     data = dict(
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.md5hash = ""
    #     assert reference.has_hash is False
    #
    # def test_has_hash_not_empty(self):
    #     data = dict(
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.md5hash = "123"
    #     assert reference.has_hash is True
    #
    # def test_has_hash_is_none(self):
    #     data = dict(
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.md5hash = None
    #     assert reference.has_hash is False

    # def test_cite_dictionary(self):
    #     """this tests https://en.wikipedia.org/wiki/Template:Cite_dictionary which is an alias for cite encyclopedia"""
    #     data = dict(
    #         # oclc="test",
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite dictionary",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     assert reference.has_hash is True
    #     assert reference.md5hash == "9fe13e5007b27e99897000a584bf631d"

    # def test_cite_q(self):
    #     """this tests https://en.wikipedia.org/wiki/Template:Cite_q"""
    #     raw_template = "{{citeq|Q1}}"
    #     raw_reference = f"<ref>{raw_template}</ref>"
    #     wikicode = parse(raw_reference)
    #     refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
    #     for ref in refs:
    #         raw_reference_object = WikipediaReference(
    #             wikicode=ref,
    #             testing=True,
    #             # wikibase=wikibase
    #         )
    #         # This also runs finish_parsing_and_generate_hash()
    #         reference = raw_reference_object.get_finished_wikipedia_reference_object()
    #         assert reference.number_of_templates == 1
    #         assert reference.templates[0].raw_template == raw_template
    #         assert reference.first_parameter == "Q1"
    #         assert reference.wikidata_qid == "Q1"
    #         assert reference.is_valid_qid is True
    #         # assert reference.has_hash is True
    #         # assert reference.md5hash == "9fe13e5007b27e99897000a584bf631d"

    # def test_combined_url_isbn_template_reference(self):
    #     wikitext = ("<ref>{{url|http://example.com}}{{isbn|1234}}</ref>",)
    #     wikicode = parse(wikitext)
    #     refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
    #     for ref in refs:
    #         raw_reference_object = WikipediaReference(
    #             wikicode=ref,
    #             testing=True,
    #             # wikibase=wikibase
    #         )
    #         # This also runs finish_parsing_and_generate_hash()
    #         reference = raw_reference_object.get_finished_wikipedia_reference_object()
    #         assert reference
    #         assert reference.number_of_templates == 2
    #         assert reference.isbn == "1234"

    # def test_get_qid_from_multitemplate_reference(self):
    #     wikitext = ("<ref>{{url|http://example.com}}{{citeq|Q1}}</ref>",)
    #     wikicode = parse(wikitext)
    #     refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
    #     for ref in refs:
    #         raw_reference_object = WikipediaReference(
    #             wikicode=ref,
    #             testing=True,
    #             # wikibase=wikibase
    #         )
    #         # This also runs finish_parsing_and_generate_hash()
    #         raw_reference_object.extract_and_check()
    #         assert raw_reference_object.extraction_done is True
    #         # for templates in raw_reference_object.templates:
    #         #     assert templates.extraction_done is True
    #         reference = raw_reference_object.get_finished_wikipedia_reference_object()
    #         assert reference.number_of_templates == 2
    #         assert reference.multiple_templates_found is True
    #         # assert reference.wikidata_qid == "Q1"

    # def test_validate_qid_valid(self):
    #     raw_template = "{{citeq|Q1}}"
    #     raw_reference = f"<ref>{raw_template}</ref>"
    #     wikicode = parse(raw_reference)
    #     refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
    #     for ref in refs:
    #         raw_reference_object = WikipediaReference(
    #             wikicode=ref,
    #             testing=True,
    #             # wikibase=wikibase
    #         )
    #         # This also runs finish_parsing_and_generate_hash()
    #         reference = raw_reference_object.get_finished_wikipedia_reference_object()
    #         assert reference.is_valid_qid is True

    # def test_validate_qid_invalid(self):
    #     raw_template = "{{citeq|Q1s}}"
    #     raw_reference = f"<ref>{raw_template}</ref>"
    #     wikicode = parse(raw_reference)
    #     refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
    #     for ref in refs:
    #         raw_reference_object = WikipediaReference(
    #             wikicode=ref,
    #             testing=True,
    #             # wikibase=wikibase
    #         )
    #         # This also runs finish_parsing_and_generate_hash()
    #         reference = raw_reference_object.get_finished_wikipedia_reference_object()
    #         assert reference.is_valid_qid is False

    # def test___get_url__(self):
    #     """We don't support multiple url templates in a single reference"""
    #     wikitext = ("<ref>{{url|http://example.com}}{{url|1234}}</ref>",)
    #     wikicode = parse(wikitext)
    #     refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
    #     for ref in refs:
    #         raw_reference_object = WikipediaReference(
    #             wikicode=ref,
    #             testing=True,
    #             # wikibase=wikibase
    #         )
    #         # This also runs finish_parsing_and_generate_hash()
    #         ref = raw_reference_object.get_finished_wikipedia_reference_object()
    #         assert ref.encountered_parse_error is True

    # def test___get_isbn__(self):
    #     """We don't support multiple isbn templates in a single reference"""
    #     wikitext = ("<ref>{{isbn|4321}}{{isbn|1234}}</ref>",)
    #     wikicode = parse(wikitext)
    #     refs = wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
    #     for ref in refs:
    #         raw_reference_object = WikipediaReference(
    #             wikicode=ref,
    #             testing=True,
    #             # wikibase=wikibase
    #         )
    #         # This also runs finish_parsing_and_generate_hash()
    #         ref = raw_reference_object.get_finished_wikipedia_reference_object()
    #         assert ref.encountered_parse_error is True

    def test__extract_raw_templates_one(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            # print(ref)
            raw_reference_object = WikipediaReference(tag=ref)
            raw_reference_object.__extract_raw_templates__()
            assert raw_reference_object.number_of_templates == 1
            assert raw_reference_object.templates[0].raw_template == raw_template

    def test_extract_raw_templates_multiple_templates(self):
        raw_template1 = "{{citeq|Q1}}"
        raw_template2 = "{{citeq|Q2}}"
        raw_reference = f"<ref>{raw_template1 + raw_template2}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaReference(tag=ref)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.number_of_templates == 2
            assert raw_reference_object.multiple_templates_found is True

    def test___determine_reference_type_one_template(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaReference(tag=ref)
            raw_reference_object.extract_and_check()
            # assert raw_reference_object.citeq_template_found is True
        raw_template = "{{cite q|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaReference(tag=ref)
            raw_reference_object.extract_and_check()
            # assert raw_reference_object.citeq_template_found is True

    def test___determine_reference_type_cite_q_extra_params(self):
        url = "http://example.com"
        raw_template = f"{{{{citeq|Q1|url={url}}}}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaReference(tag=ref)
            raw_reference_object.extract_and_check()
            # assert raw_reference_object.citeq_template_found is True
            assert (
                raw_reference_object.templates[0].parameters["first_parameter"] == "Q1"
            )
            assert raw_reference_object.templates[0].parameters["url"] == url

    def test___determine_reference_type_two_templates(self):
        raw_template1 = "{{citeq|Q1}}"
        raw_template2 = "{{citeq|Q2}}"
        raw_reference = f"<ref>{raw_template1 + raw_template2}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaReference(tag=ref)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.number_of_templates == 2
            assert raw_reference_object.multiple_templates_found is True

    def test_number_of_templates_one(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaReference(tag=ref)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.number_of_templates == 1

    def test_number_of_templates_two(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template + raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaReference(tag=ref)
            raw_reference_object.__extract_templates_and_parameters__()
            assert raw_reference_object.number_of_templates == 2
            assert raw_reference_object.multiple_templates_found is True

    def test_get_wikipedia_reference_object_citeq(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            reference = WikipediaReference(tag=ref, testing=True)
            reference.extract_and_check()
            assert reference.number_of_templates == 1
            assert reference.templates[0].name == "citeq"
            assert reference.number_of_templates == 1
            assert reference.templates[0].raw_template == raw_template
            assert reference.templates[0].name == "citeq"
            # assert reference.wikidata_qid == "Q1"

    def test_first_template_name(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        wikicode = parse(raw_reference)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            reference = WikipediaReference(tag=ref, testing=True)
            reference.extract_and_check()
            assert reference.number_of_templates == 1
            assert reference.templates[0].name == "citeq"
            assert reference.number_of_templates == 1
            assert reference.templates[0].raw_template == raw_template
            assert reference.templates[0].name == "citeq"

    def test_named_reference(self):
        ref = '<ref name="INE"/>'
        wikicode = parse(ref)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaReference(tag=ref, testing=True)
            raw_reference_object.extract_and_check()
            assert raw_reference_object.is_empty_named_reference is True

    def test_get_wikicode_as_string_empty(self):
        ref = '<ref name="INE"/>'
        wikicode = parse(ref)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            print(ref)
            raw_reference_object = WikipediaReference(tag=ref, testing=True)
            assert raw_reference_object.get_wikicode_as_string == ref

    def test_get_wikicode_as_string_nonempty(self):
        wikitext = (
            '<ref name="jew virt lib">[http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour'
            ' "IAF Aircraft Inventory: Sud-Ouest S.O. 4050 Vautour."] Jewish Virtual Library, '
            "Retrieved: 16 September 2017.</ref>"
        )
        wikicode = parse(wikitext)
        refs = wikicode.filter_tags(matches=lambda tag: tag.lower() == "ref")
        for ref in refs:
            raw_reference_object = WikipediaReference(tag=ref, testing=True)
            assert raw_reference_object.get_wikicode_as_string == ref

    def test_is_footnote_reference(self):
        ref = "{{citeq|Q1}}"
        wikicode = parse(ref)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        assert raw_reference_object.is_footnote_reference is False
        assert raw_reference_object.is_general_reference is True

    def test_is_cs1_reference(self):
        wikitext = (
            "* {{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
        assert raw_reference_object.is_general_reference is True
        # assert raw_reference_object.cs1_template_found is True

    # def test__plain_text_detected_before(self):
    #     wikitext = (
    #         "test{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.plain_text_in_reference is True
    #
    # def test__plain_text_detected_after(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong}}test"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.plain_text_in_reference is True
    #
    # def test__plain_text_detected_no(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.plain_text_in_reference is False

    # def test_wayback_url_true(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
    #         "|url=http://web.archive.org/web/19970222174751/https://www1.geocities.com/}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         section="test",
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     raw_reference_object.extract_and_check()
    # assert raw_reference_object.web_archive_org_in_reference is True

    # def test_wayback_url_false(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
    #         "|url=https://www1.geocities.com/}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     raw_reference_object.extract_and_check()
    # assert raw_reference_object.web_archive_org_in_reference is False

    # def test_archive_details_url_true(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
    #         "|url=https://archive.org/details/delattre00herruoft}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.archive_org_slash_details_in_reference is True

    # def test_archive_details_url_false(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
    #         "|url=https://www1.geocities.com/}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.archive_org_slash_details_in_reference is False
    #
    # def test_google_books_url_true(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
    #         "|url=https://books.google.se/books?id=9HRodACJLOoC&printsec="
    #         "frontcover&dq=test&hl=sv&sa=X&redir_esc=y#v=onepage&q=test&f=false}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.google_books_url_or_template_found is True
    #
    # def test_google_books_url_false(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
    #         "|url=https://www1.geocities.com/}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.google_books_url_or_template_found is False
    #
    # def test_google_books_template_found_true(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
    #         "|url={{google books |plainurl=y |id=CDJpAAAAMAAJ |page=313}}}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.google_books_template_found is True
    #
    # def test_google_books_template_found_false(self):
    #     wikitext = (
    #         "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
    #         "|url=https://www1.geocities.com/}}"
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.google_books_template_found is False

    def test_template_first_level_domains_one(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://www1.geocities.com/}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
        assert raw_reference_object.unique_first_level_domains == ["geocities.com"]

    def test_template_first_level_domains_two(self):
        wikitext = (
            "{{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorong"
            "|url=https://www1.geocities.com/|archive-url=https://web.archive.org/web/19961022173245/https://www1.geocities.com/}}"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
        # archive.org should not appear here
        assert raw_reference_object.unique_first_level_domains == [
            "geocities.com",
        ]

    def test___find_bare_urls_outside_templates_none_(self):
        """Test on a reference from the wild"""
        wikitext = (
            '<ref name="jew virt lib">'
            "[http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour"
            ' "IAF Aircraft Inventory: Sud-Ouest S.O. 4050 Vautour."] Jewish Virtual Library, '
            "Retrieved: 16 September 2017.</ref>"
        )
        wikicode = parse(wikitext)
        reference = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        bare_urls = reference.__find_bare_urls_outside_templates__()
        assert len(bare_urls) == 0

    def test___find_bare_urls_outside_templates_one_(self):
        """Test on a reference from the wild"""
        wikitext = (
            '<ref name="jew virt lib">'
            "http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour"
            ' "IAF Aircraft Inventory: Sud-Ouest S.O. 4050 Vautour." Jewish Virtual Library, '
            "Retrieved: 16 September 2017.</ref>"
        )
        wikicode = parse(wikitext)
        reference = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        bare_urls = reference.__find_bare_urls_outside_templates__()
        assert len(bare_urls) == 1

    def test___external_links_in_reference__(self):
        """Test on a reference from the wild"""
        wikitext = (
            '<ref name="jew virt lib">[http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour'
            ' "IAF Aircraft Inventory: Sud-Ouest S.O. 4050 Vautour."] Jewish Virtual Library, '
            "Retrieved: 16 September 2017.</ref>"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaReference(
            wikicode=wikicode, testing=True, is_general_reference=True, section="test"
        )
        raw_reference_object.__extract_external_wikicoded_links_from_the_reference__()
        assert len(raw_reference_object.wikicoded_links) == 1
        assert raw_reference_object.wikicoded_links[0] == WikipediaUrl(
            url="http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour"
        )

    # def test_multiple_cs1_templates(self):
    #     """This is a multitemplate reference of a special kind which we should detect
    #     It overcomplicates for us and should really be split into multiple <ref>
    #     references by the community if there is a consensus for that.
    #
    #     The only way to detect it is to count if multiple cs1 templates
    #     are found in the same reference"""
    #     data = (
    #         '<ref name="territory">'
    #         "*{{Cite web|last=Benedikter|first=Thomas|date=19 June 2006|"
    #         "title=The working autonomies in Europe|"
    #         "url=http://www.gfbv.it/3dossier/eu-min/autonomy.html|publisher=[[Society for Threatened Peoples]]|"
    #         "quote=Denmark has established very specific territorial autonomies with its two island territories|"
    #         "access-date=8 June 2012|archive-date=9 March 2008|"
    #         "archive-url=https://web.archive.org/web/20080309063149/http://www.gfbv.it/3dossier/eu-min/autonomy."
    #         "html|url-status=dead}}"
    #         "*{{Cite web|last=Ackrén|first=Maria|date=November 2017|"
    #         "title=Greenland|url=http://www.world-autonomies.info/tas/Greenland/Pages/default.aspx|"
    #         "url-status=dead|archive-url=https://web.archive.org/web/20190830110832/http://www.world-"
    #         "autonomies.info/tas/Greenland/Pages/default.aspx|archive-date=30 August 2019|"
    #         "access-date=30 August 2019|publisher=Autonomy Arrangements in the World|quote=Faroese and "
    #         "Greenlandic are seen as official regional languages in the self-governing territories "
    #         "belonging to Denmark.}}"
    #         "*{{Cite web|date=3 June 2013|title=Greenland|"
    #         "url=https://ec.europa.eu/europeaid/countries/greenland_en|access-date=27 August 2019|"
    #         "website=International Cooperation and Development|publisher=[[European Commission]]|"
    #         "language=en|quote=Greenland [...] is an autonomous territory within the Kingdom of Denmark}}</ref>"
    #     )
    #     wikicode = parse(data)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode, testing=True, check_urls=False
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.number_of_cs1_templates == 3
    #     assert raw_reference_object.multiple_cs1_templates_found is True

    # def test_number_of_templates_missing_first_parameter_zero(self):
    #     data = (
    #         "<ref>{{url|1=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 <!--|alternate-full-text-url="
    #         "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 -->}}</ref>"
    #     )
    #     wikicode = parse(data)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode, testing=True, check_urls=False
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.number_of_templates == 1
    #     assert raw_reference_object.number_of_templates_missing_first_parameter == 0

    # def test_number_of_templates_missing_first_parameter_one(self):
    #     data = "<ref>{{url}}</ref>"
    #     wikicode = parse(data)
    #     raw_reference_object = WikipediaReference(
    #         wikicode=wikicode, testing=True, check_urls=False
    #     )
    #     raw_reference_object.extract_and_check()
    #     assert raw_reference_object.number_of_templates == 1
    #     print(raw_reference_object.templates[0].dict())
    #     assert raw_reference_object.number_of_templates_missing_first_parameter == 1

    def test_get_template_dicts_cite_book(self):
        data = (
            '<ref name="Wilson">{{cite book | title = Bicycling Science | '
            "url = https://archive.org/details/isbn_9780262731546 | url-access = "
            "registration | edition = Third | last = Wilson | first = David Gordon |"
            "author2=Jim Papadopoulos | year = 2004 | publisher = The MIT Press | "
            "isbn = 978-0-262-73154-6 | pages = "
            "[https://archive.org/details/isbn_9780262731546/page/270 270–72]}}</ref>"
        )
        wikicode = parse(data)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
        assert raw_reference_object.get_template_dicts == [
            {
                "parameters": OrderedDict(
                    [
                        ("title", "Bicycling Science"),
                        ("url", "https://archive.org/details/isbn_9780262731546"),
                        ("url_access", "registration"),
                        ("edition", "Third"),
                        ("last", "Wilson"),
                        ("first", "David Gordon"),
                        ("author2", "Jim Papadopoulos"),
                        ("year", "2004"),
                        ("publisher", "The MIT Press"),
                        ("isbn", "978-0-262-73154-6"),
                        (
                            "pages",
                            "[https://archive.org/details/isbn_9780262731546/page/270 270–72]",
                        ),
                        ("template_name", "cite book"),
                    ]
                ),
                "isbn": "978-0-262-73154-6",
            }
        ]

    def test_unique_first_level_domains(self):
        data = (
            '<ref name="Wilson">{{cite book | title = Bicycling Science | '
            "url = https://archive.org/details/isbn_9780262731546 | url-access = "
            "registration | edition = Third | last = Wilson | first = David Gordon |"
            "author2=Jim Papadopoulos | year = 2004 | publisher = The MIT Press | "
            "isbn = 978-0-262-73154-6 | pages = "
            "[https://archive.org/details/isbn_9780262731546/page/270 270–72]}}</ref>"
        )
        wikicode = parse(data)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
        # archive.org should only appear once
        assert raw_reference_object.unique_first_level_domains == ["archive.org"]

    # def test__find_bare_urls_in_comments_none_(self):
    #     """mwparserfromhell does not seem to support comments inside templates currently"""
    #     wikitext = (
    #         "<ref>{{url|1=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 <!--|alternate-full-text-url="
    #         "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 -->}}</ref>"
    #     )
    #     wikicode = parse(wikitext)
    #     reference_object = WikipediaReference(
    #         section="test",
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     console.print(wikicode)
    #     urls = reference_object.__find_bare_urls_in_comments__()
    #     assert len(urls) == 0

    # TODO investigate failure and report bug upstream?
    # def test__find_bare_urls_in_comments_one_(self):
    #     """mwparserfromhell does not seem to support comments outside templates currently"""
    #     wikitext = (
    #         "<ref>{{url|1=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 }} <!-- "
    #         "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 --></ref>"
    #     )
    #     wikicode = parse(wikitext)
    #     reference_object = WikipediaReference(
    #         section="test",
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     console.print(wikicode)
    #     urls = reference_object.__find_bare_urls_in_comments__()
    #     assert len(urls) == 1

    def test_unique_first_level_domains2(self):
        """This test is affected by the inability of mwparserfromhell to parse comments inside templates"""
        wikitext = (
            "<ref>{{url|1=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 <!--|alternate-full-text-url="
            "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 -->}}</ref>"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
        assert len(raw_reference_object.raw_urls) == 1
        assert len(raw_reference_object.unique_first_level_domains) == 1

    def test_name_exists(self):
        data = (
            '<ref name="Wilson">{{cite book | title = Bicycling Science | '
            "url = https://archive.org/details/isbn_9780262731546 | url-access = "
            "registration | edition = Third | last = Wilson | first = David Gordon |"
            "author2=Jim Papadopoulos | year = 2004 | publisher = The MIT Press | "
            "isbn = 978-0-262-73154-6 | pages = "
            "[https://archive.org/details/isbn_9780262731546/page/270 270–72]}}</ref>"
        )
        wikicode = parse(data)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
        assert raw_reference_object.get_name == "Wilson"

    def test_name_exists_slash(self):
        data = '<ref name="Wilson"\\>'
        wikicode = parse(data)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
        assert raw_reference_object.get_name == "Wilson"

    def test_name_exists_forward_slash(self):
        """test edge case with missing quotes"""
        data = "<ref name=terry_hunt/>"
        wikicode = parse(data)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
        assert raw_reference_object.get_name == "terry_hunt"

    def test_name_none(self):
        wikitext = (
            "<ref>{{url|1=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 <!--|alternate-full-text-url="
            "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 -->}}</ref>"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        raw_reference_object.extract_and_check()
        assert raw_reference_object.get_name == ""

    def test___find_bare_urls_outside_templates_none2_(self):
        wikitext = (
            "* {{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's "
            "Rongorongo Inscriptions|journal= Journal of the Polynesian Society "
            "|issue=104|pages=303–21|url="
            "http://www.jps.auckland.ac.nz/document/Volume_104_1995"
            "/Volume_104%2C_No._3/Preliminary_evidence_for_cosmogonic_texts_"
            "in_Rapanui%26apos%3Bs_Rongorongo_inscriptions%2C_by_Steven_"
            "Roger_Fischer%2C_p_303-322/p1}} "
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        assert raw_reference_object.__find_bare_urls_outside_templates__() == []

    def test___find_bare_urls_outside_templates_one2_(self):
        wikitext = (
            "* {{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
            "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's "
            "Rongorongo Inscriptions|journal= Journal of the Polynesian "
            "Society |issue=104|pages=303–21|url="
            "http://www.jps.auckland.ac.nz/document/Volume_104_1995"
            "/Volume_104%2C_No._3/Preliminary_evidence_for_cosmogoni"
            "c_texts_in_Rapanui%26apos%3Bs_Rongorongo_inscriptions%2C_"
            "by_Steven_Roger_Fischer%2C_p_303-322/p1}} http://www.jps.auckland.ac.nz"
        )
        wikicode = parse(wikitext)
        raw_reference_object = WikipediaReference(
            section="test",
            wikicode=wikicode,
            testing=True,
            is_general_reference=True,
        )
        assert raw_reference_object.__find_bare_urls_outside_templates__() == [
            "http://www.jps.auckland.ac.nz"
        ]

    # def test___find_bare_urls_in_comments_none_(self):
    #     wikitext = (
    #         "* {{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanu"
    #         "i's Rongorongo Inscriptions|journal= Journal of the Polynes"
    #         "ian Society |issue=104|pages=303–21|url="
    #         "http://www.jps.auckland.ac.nz/document/Volume_104_1995"
    #         "/Volume_104%2C_No._3/Preliminary_evidence_for_cosmogonic_te"
    #         "xts_in_Rapanui%26apos%3Bs_Rongorongo_inscriptions%2C_by_Ste"
    #         "ven_Roger_Fischer%2C_p_303-322/p1}} "
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         section="test",
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     assert raw_reference_object.__find_bare_urls_in_comments__() == []

    # def test___find_bare_urls_in_comments_one_(self):
    #     # TODO report this as a bug upstream because mwparserfromhell cannot find the comment
    #     wikitext = (
    #         "* {{cite journal|last= Fischer|first= Steven Roger|year= 1995|"
    #         "title= Preliminary Evidence for Cosmogonic Texts in Rapanui's Rongorongo "
    #         "Inscriptions|journal= Journal of the Polynesian Society |issue=104|pages=303–21|url="
    #         "http://www.jps.auckland.ac.nz/document/Volume_104_1995"
    #         "/Volume_104%2C_No._3/Preliminary_evidence_for_cosmogonic_texts_in_Rapanui%26apos%"
    #         "3Bs_Rongorongo_inscriptions%2C_by_Steven_Roger_Fischer%2C_p_303-322/p1 <!-- test comment with a url http://www.jps.auckland.ac.nz -->}} "
    #     )
    #     wikicode = parse(wikitext)
    #     raw_reference_object = WikipediaReference(
    #         section="test",
    #         wikicode=wikicode,
    #         testing=True,
    #         is_general_reference=True,
    #     )
    #     assert len(raw_reference_object.__find_bare_urls_in_comments__()) == 1
