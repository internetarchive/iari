from unittest import TestCase

from src import IASandboxWikibase, console
from src.helpers.template_extraction import extract_templates_and_params
from src.models.wikimedia.wikipedia.reference.english.google_books import (
    GoogleBooks,
    GoogleBooksSchema,
)


class TestGoogleBooks(TestCase):
    def test_parsing_into_object_numeric_page(self):
        data = "{{google books |plainurl=y |id=CDJpAAAAMAAJ |page=313}}"
        template_tuples = extract_templates_and_params(data, True)
        for _template_name, content in template_tuples:
            gb: GoogleBooks = GoogleBooksSchema().load(content)
            gb.wikibase = IASandboxWikibase()
            gb.finish_parsing()
            console.print(gb.dict())
            assert gb.url == "https://books.google.com/books?id=CDJpAAAAMAAJ"

    def test_parsing_into_object_with_non_numeric_page(self):
        data = "{{google books |plainurl=y |id=CDJpAAAAMAAJ |page=313d}}"
        template_tuples = extract_templates_and_params(data, True)
        for _template_name, content in template_tuples:
            gb: GoogleBooks = GoogleBooksSchema().load(content)
            gb.wikibase = IASandboxWikibase()
            gb.finish_parsing()
            console.print(gb.dict())
            assert gb.url == "https://books.google.com/books?id=CDJpAAAAMAAJ"

    def test_id_with_too_many_chars(self):
        data = "{{google books |plainurl=y |id=CDJpAAAAMAAJTEST |page=313d}}"
        template_tuples = extract_templates_and_params(data, True)
        for _template_name, content in template_tuples:
            GoogleBooksSchema().load(content)

    def test_id_with_too_few_chars(self):
        data = "{{google books |plainurl=y |id=CDJpAAAAMAA |page=313d}}"
        template_tuples = extract_templates_and_params(data, True)
        for _template_name, content in template_tuples:
            GoogleBooksSchema().load(content)
