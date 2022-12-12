import logging
from datetime import date, timezone
from typing import List
from unittest import TestCase

from dateutil.parser import isoparse  # type: ignore
from wikibaseintegrator import WikibaseIntegrator  # type: ignore
from wikibaseintegrator.models import Claim  # type: ignore

import config
from src.helpers.console import console
from src.helpers.wbi import get_item_value
from src.models.return_ import Return
from src.models.return_.wikibase_return import WikibaseReturn
from src.models.wikibase.crud import WikibaseCrud
from src.models.wikibase.crud.create import WikibaseCrudCreate
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.wikipedia.article import WikipediaArticle
from src.models.wikimedia.wikipedia.reference.english.english_reference import (
    EnglishWikipediaReference,
)

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWikibaseCrudCreate(TestCase):
    def test_prepare_new_reference_item(self):
        """This tests both full name string generation and archive qualifier generation"""
        wc = WikibaseCrud(wikibase=IASandboxWikibase())
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Democracy")
        wppage.__get_wikipedia_article_from_title__()
        reference = EnglishWikipediaReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
                "archive_url": "https://web.archive.org/web/20190701062212/http://www.mgtrust.org/ind1.htm",
            }
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        logger.debug(
            f"reference.detected_archive_of_archive_url: {reference.detected_archive_of_archive_url}"
        )
        assert reference.detected_archive_of_archive_url is not None
        assert len(reference.persons_without_role) > 0
        item = wc.__prepare_new_reference_item__(page_reference=reference)
        console.print(item.get_json())
        assert item.claims.get(property=wc.wikibase.FULL_NAME_STRING) is not None
        assert item.claims.get(property=wc.wikibase.ARCHIVE_URL) is not None
        assert (
            item.claims.get(property=wc.wikibase.ARCHIVE_URL)[0].qualifiers.get(
                property=wc.wikibase.ARCHIVE
            )
            is not None
        )

    def test_prepare_new_reference_item_with_very_long_title(self):
        wc = WikibaseCrud(wikibase=IASandboxWikibase())
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Test")
        wppage.__get_wikipedia_article_from_title__()
        reference = EnglishWikipediaReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": (
                    "Analytical Theory of Democracy: "
                    "History, Mathematics and Applications Analytical "
                    "Theory of Democracy: History, "
                    "Mathematics and Applications Analytical Theory of "
                    "Theory of Democracy: History, "
                    "Mathematics and Applications Analytical Theory of "
                    "Democracy: History, Mathematics and Applications"
                ),
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
            }
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        item = wc.__prepare_new_reference_item__(page_reference=reference)
        # console.print(item.get_json())
        assert len(item.labels.get(language="en")) == 250

    def test_prepare_new_wikipedia_article_item_invalid_qid(self):
        wc = WikibaseCrud(wikibase=IASandboxWikibase())
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Democracy")
        wppage.__get_wikipedia_article_from_title__()
        reference = EnglishWikipediaReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
            }
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        reference.return_ = WikibaseReturn(item_qid="test", uploaded_now=False)
        wppage.references = []
        wppage.references.append(reference)
        with self.assertRaises(ValueError):
            wc.max_number_of_item_citations = 0
            wc.__prepare_new_wikipedia_article_item__(
                wikipedia_article=wppage,
            )
        # console.print(item.get_json())

        # logger.info(f"url: {wppage.wikicitations_url}")

    def test_prepare_new_wikipedia_article_item_valid_qid(self):
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Democracy")
        wppage.__get_wikipedia_article_from_title__()
        reference = EnglishWikipediaReference(
            **{
                "last": "Tangian",
                "first": "Andranik",
                "date": "2020",
                "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
                "series": "Studies in Choice and Welfare",
                "publisher": "Springer",
                "location": "Cham, Switzerland",
                "isbn": "978-3-030-39690-9",
                "doi": "10.1007/978-3-030-39691-6",
                "s2cid": "216190330",
                "template_name": "cite book",
            }
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        reference.return_ = WikibaseReturn(item_qid="Q1", uploaded_now=False)
        wppage.references = []
        wppage.references.append(reference)
        wppage.__generate_hash__()
        # with self.assertRaises(ValueError):
        wc = WikibaseCrudCreate(wikibase=IASandboxWikibase())
        item = wc.__prepare_new_wikipedia_article_item__(
            wikipedia_article=wppage,
        )
        # console.print(item.get_json())
        # assert item.labels.get("en") == title
        citations: List[Claim] = item.claims.get(wc.wikibase.CITATIONS)
        # console.print(citations[0].mainsnak.datavalue["value"]["id"])
        assert citations[0].mainsnak.datavalue["value"]["id"] == "Q1"
        # logger.info(f"url: {wppage.wikicitations_url}")

    # @pytest.mark.xfail(bool(getenv("CI")), reason="GitHub Actions do not have logins")
    # def test_prepare_and_upload_wikipedia_page_item_valid_qid(self):
    #     wppage = WikipediaArticle(wikibase=IASandboxWikibase())
    #     title = "Democracy"
    #     wppage.__get_wikipedia_article_from_title__(title=title)
    #     wppage.__generate_hash__()
    #     reference = EnglishWikipediaReference(
    #         **{
    #             "last": "Tangian",
    #             "first": "Andranik",
    #             "date": "2020",
    #             "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
    #             "series": "Studies in Choice and Welfare",
    #             "publisher": "Springer",
    #             "location": "Cham, Switzerland",
    #             "isbn": "978-3-030-39690-9",
    #             "doi": "10.1007/978-3-030-39691-6",
    #             "s2cid": "216190330",
    #             "template_name": "cite book",
    #         }
    #     )
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     test_qid = "Q4"
    #     reference.wikicitations_qid = test_qid
    #     wppage.references = []
    #     wppage.references.append(reference)
    #     wikibase = IASandboxWikibase()
    #     wcr = WikibaseCrudRead(wikibase=wikibase)
    #     wcr.prepare_and_upload_wikipedia_page_item(
    #         wikipedia_article=wppage,
    #     )
    #     items = wcr.__get_all_items__(item_type=wikibase.WIKIPEDIA_PAGE)
    #     assert items and len(items) == 1

    def test_prepare_and_upload_website_item(self):
        wc = WikibaseCrudCreate(wikibase=IASandboxWikibase())
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Democracy")
        wppage.__get_wikipedia_article_from_title__()
        wppage.__generate_hash__()
        # This reference is the first one on https://en.wikipedia.org/w/index.php?title=Democracy&action=edit
        reference = EnglishWikipediaReference(
            **{
                "agency": "Oxford University Press",
                "access-date": "24 February 2021",
                "title": "Democracy",
                "template_name": "cite news",
                "url": "https://www.oxfordreference.com/view/10.1093/acref/9780195148909.001.0001/acref-9780195148909-e-241",
            }
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        return_: Return = wc.prepare_and_upload_website_item(
            page_reference=reference, wikipedia_article=wppage
        )
        assert return_.item_qid is not None
        # bot = WcdImportBot(wikibase=IASandboxWikibase())
        # bot.rinse_all_items_and_cache()

    # @pytest.mark.xfail(bool(getenv("CI")), reason="GitHub Actions do not have logins")
    # def test_uploading_a_page_reference_and_website_item(self):
    #     # wcd = WikibaseCrudDelete(wikibase=IASandboxWikibase())
    #     # wcd.delete_imported_items()
    #     wppage = WikipediaArticle(wikibase=IASandboxWikibase())
    #     title = "Democracy"
    #     wppage.__get_wikipedia_article_from_title__(title=title)
    #     wppage.__generate_hash__()
    #     # This reference is the first one on https://en.wikipedia.org/w/index.php?title=Democracy&action=edit
    #     reference = EnglishWikipediaReference(
    #         **{
    #             "agency": "Oxford University Press",
    #             "access-date": "24 February 2021",
    #             "title": "Democracy",
    #             "template_name": "cite news",
    #             "url": "https://www.oxfordreference.com/view/10.1093/acref/9780195148909.001.0001/acref-9780195148909-e-241",
    #         }
    #     )
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     wppage.references = []
    #     wppage.references.append(reference)
    #     wppage.__upload_references_and_websites_if_missing__()
    #     console.print(
    #         f"Waiting {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
    #     )
    #     sleep(config.sparql_sync_waiting_time_in_seconds)
    #     wcr = WikibaseCrudRead(wikibase=IASandboxWikibase())
    #     items = wcr.__get_all_items__(item_type=IASandboxWikibase().WEBSITE_ITEM)
    #     assert len(items) == 1
    #     ref_items = wcr.__get_all_items__(
    #         item_type=IASandboxWikibase().WIKIPEDIA_REFERENCE
    #     )
    #     assert len(ref_items) == 1

    def test_uploading_a_page_reference_and_website_item_twice(self):
        # wcd = WikibaseCrudDelete(wikibase=IASandboxWikibase())
        # wcd.delete_imported_items()
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Democracy")
        wppage.__get_wikipedia_article_from_title__()
        wppage.__generate_hash__()
        wppage.__setup_cache__()
        # This reference is the first one on https://en.wikipedia.org/w/index.php?title=Democracy&action=edit
        reference = EnglishWikipediaReference(
            **{
                "agency": "Oxford University Press",
                "access-date": "24 February 2021",
                "title": "Democracy",
                "template_name": "cite news",
                "url": "https://www.oxfordreference.com/view/10.1093/acref/9780195148909.001.0001/acref-9780195148909-e-241",
            }
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        wppage.references = []
        wppage.references.append(reference)
        wppage.references.append(reference)
        wppage.__upload_references_and_websites_if_missing__(testing=True)
        # We have no assertions in this test.
        # It is successful if no exceptions other than
        # NonUniqueLabelDescriptionPairError are raised.

    def test_publisher_and_location_statements(self):
        data = dict(
            access_date="2010-11-09",
            archive_date="2010-08-12",
            archive_url="https://web.archive.org/web/20100812051822/http://www.kmk.a.se/ImageUpload/kmkNytt0110.pdf",
            author2="Nynäshamns Posten",
            date="January 2010",
            first="Helene",
            language="Swedish",  # not imported
            last="Skoglund",
            location="Stockholm",
            pages="4–7",
            publisher="Kungliga Motorbåt Klubben",
            template_name="cite web",
            title="Musköbasen 40 år",
            trans_title="Muskö Naval Base 40 years",  # not imported
            url="http://www.kmk.a.se/ImageUpload/kmkNytt0110.pdf",
            url_status="dead",  # not imported
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Test")
        wppage.references.append(reference)
        wppage.extract_and_parse_and_upload_missing_items_to_wikibase()
        wbi = WikibaseIntegrator()
        wcdqid = wppage.references[0].return_.item_qid
        console.print(wppage.wikibase.entity_url(item_id=wcdqid))
        item = wbi.item.get(wcdqid)
        wikibase_access_date = wppage.wikibase.parse_time_from_claim(
            item.claims.get(wppage.wikibase.ACCESS_DATE)[0]
        )
        # https://docs.python.org/3.10/library/datetime.html#datetime.datetime.astimezone
        access_date = isoparse(data["access_date"]).replace(tzinfo=timezone.utc)
        console.print(access_date)
        assert access_date == wikibase_access_date
        archive_url: List[Claim] = item.claims.get(property=wppage.wikibase.ARCHIVE_URL)
        assert archive_url[0].mainsnak.datavalue["value"] == data["archive_url"]
        # Check also that a qualifier is present
        assert archive_url[0].qualifiers is not None
        # assert item.claims.get(property=wppage.wikibase.LANGUAGE)[0].mainsnak.datavalue["value"] == data["language"]
        assert (
            item.claims.get(property=wppage.wikibase.LOCATION_STRING)[
                0
            ].mainsnak.datavalue["value"]
            == data["location"]
        )
        # Not implemented yet
        # assert (
        #     item.claims.get(property=wppage.wikibase.PAGES)[0].mainsnak.datavalue[
        #         "value"
        #     ]
        #     == data["pages"]
        # )
        wikibase_publication_date = wppage.wikibase.parse_time_from_claim(
            item.claims.get(wppage.wikibase.PUBLICATION_DATE)[0]
        )
        assert reference.publication_date == wikibase_publication_date
        assert (
            item.claims.get(property=wppage.wikibase.PUBLISHER_STRING)[
                0
            ].mainsnak.datavalue["value"]
            == data["publisher"]
        )
        assert (
            item.claims.get(property=wppage.wikibase.TEMPLATE_NAME)[
                0
            ].mainsnak.datavalue["value"]
            == data["template_name"]
        )
        assert (
            item.claims.get(property=wppage.wikibase.TITLE)[0].mainsnak.datavalue[
                "value"
            ]
            == data["title"]
        )
        # assert item.claims.get(property=wppage.wikibase.TRANSLATED_TITLE)[0].mainsnak.datavalue["value"] == data["trans_title"]
        assert (
            item.claims.get(property=wppage.wikibase.URL)[0].mainsnak.datavalue["value"]
            == data["url"]
        )

    def test_internet_archive_id_statement(self):
        data = dict(
            url="https://archive.org/details/catalogueofshipw0000wils/",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Test")
        wppage.references.append(reference)
        wppage.extract_and_parse_and_upload_missing_items_to_wikibase()
        wbi = WikibaseIntegrator()
        item = wbi.item.get(wppage.references[0].return_.item_qid)
        assert (
            item.claims.get(property=wppage.wikibase.INTERNET_ARCHIVE_ID)[
                0
            ].mainsnak.datavalue["value"]
            == reference.internet_archive_id
        )

    # DEPRECATED since 2.1.0-alpha3
    # def test_google_books_id_statement(self):
    #     data = dict(
    #         url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
    #         template_name="cite book",
    #     )
    #     reference = EnglishWikipediaReference(**data)
    #     reference.wikibase = IASandboxWikibase()
    #     reference.finish_parsing_and_generate_hash(testing=True)
    #     wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Test")
    #     wppage.references.append(reference)
    #     wppage.extract_and_parse_and_upload_missing_items_to_wikibase()
    #     wbi = WikibaseIntegrator()
    #     item = wbi.item.get(wppage.references[0].return_.item_qid)
    #     assert (
    #         item.claims.get(property=wppage.wikibase.GOOGLE_BOOKS_ID)[
    #             0
    #         ].mainsnak.datavalue["value"]
    #         == reference.google_books_id
    #     )

    def test_periodical_string_statement(self):
        data = dict(
            periodical="test",
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Test")
        wppage.references.append(reference)
        wppage.extract_and_parse_and_upload_missing_items_to_wikibase()

        wbi = WikibaseIntegrator()
        wcdqid = wppage.references[0].return_.item_qid
        print(wcdqid)
        item = wbi.item.get(wcdqid)
        assert (
            item.claims.get(property=wppage.wikibase.PERIODICAL_STRING)[
                0
            ].mainsnak.datavalue["value"]
            == data["periodical"]
        )

    def test_oclc_statement(self):
        data = dict(
            oclc="test",
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Test")
        wppage.references.append(reference)
        wppage.extract_and_parse_and_upload_missing_items_to_wikibase()
        wbi = WikibaseIntegrator()
        item = wbi.item.get(wppage.references[0].return_.item_qid)
        assert (
            item.claims.get(property=wppage.wikibase.OCLC_CONTROL_NUMBER)[
                0
            ].mainsnak.datavalue["value"]
            == data["oclc"]
        )

    def test_retrieved_date_statement(self):
        data = dict(
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Test")
        wppage.references.append(reference)
        wppage.extract_and_parse_and_upload_missing_items_to_wikibase()
        wbi = WikibaseIntegrator()
        item = wbi.item.get(wppage.references[0].return_.item_qid)
        time_in_wikibase = wppage.wikibase.parse_time_from_claim(
            item.claims.get(property=wppage.wikibase.RETRIEVED_DATE)[0]
        )
        assert time_in_wikibase.date() == date.today()

    def test_wikidata_qid_statement(self):
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Test")
        wppage.extract_and_parse_and_upload_missing_items_to_wikibase()
        wbi = WikibaseIntegrator()
        item = wbi.item.get(wppage.return_.item_qid)
        assert (
            item.claims.get(property=wppage.wikibase.WIKIDATA_QID)[
                0
            ].mainsnak.datavalue["value"]
            == "Q224615"
        )

    def test_instance_of_statements(self):
        data = dict(
            oclc="test",
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash(testing=True)
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Test")
        wppage.references.append(reference)
        wppage.extract_and_parse_and_upload_missing_items_to_wikibase()
        assert wppage.references[0].has_hash is True
        assert wppage.references[0].return_ is not None
        wbi = WikibaseIntegrator()
        item = wbi.item.get(wppage.references[0].return_.item_qid)
        instance_of_value = get_item_value(
            claim=item.claims.get(property=wppage.wikibase.INSTANCE_OF)[0]
        )
        assert instance_of_value == wppage.wikibase.WIKIPEDIA_REFERENCE
        item = wbi.item.get(wppage.return_.item_qid)
        assert (
            get_item_value(
                claim=item.claims.get(property=wppage.wikibase.INSTANCE_OF)[0]
            )
            == wppage.wikibase.WIKIPEDIA_PAGE
        )

    def test_published_in_wikipedia_statement_on_article_item(self):
        """This appears on website and reference items"""
        wppage = WikipediaArticle(wikibase=IASandboxWikibase(), title="Test")
        wppage.extract_and_parse_and_upload_missing_items_to_wikibase()
        wbi = WikibaseIntegrator()
        wcdqid = wppage.return_.item_qid
        console.print(wcdqid)
        item = wbi.item.get(wcdqid)
        assert (
            item.claims.get(property=wppage.wikibase.PUBLISHED_IN)[
                0
            ].mainsnak.datavalue["value"]["id"]
            == wppage.wikibase.ENGLISH_WIKIPEDIA
        )

    # TODO test page id for articles
    # TODO test published in for references
