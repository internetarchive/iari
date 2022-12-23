from unittest import TestCase

# from mwparserfromhell import parse
#
# from src import IASandboxWikibase, console
# from src.models.wikimedia.wikipedia.reference.english.google_books import (
#     GoogleBooks,
#     GoogleBooksSchema,
# )
# from src.models.wikimedia.wikipedia.reference.template import WikipediaTemplate


class TestGoogleBooks(TestCase):
    # TODO update tests to use new Template model
    pass
    # def test_parsing_into_object_numeric_page(self):
    #     data = "{{google books |plainurl=y |id=CDJpAAAAMAAJ |page=313}}"
    #     templates = parse(data).ifilter_templates()
    #     for template in templates:
    #         wt = WikipediaTemplate(raw_template=template)
    #         wt.extract_and_prepare_parameters()
    #         gb: GoogleBooks = GoogleBooksSchema().load(content)
    #         gb.wikibase = IASandboxWikibase()
    #         gb.finish_parsing()
    #         console.print(gb.dict())
    #         assert gb.url == "https://books.google.com/books?id=CDJpAAAAMAAJ"
    #
    # def test_parsing_into_object_with_non_numeric_page(self):
    #     data = "{{google books |plainurl=y |id=CDJpAAAAMAAJ |page=313d}}"
    #     template_triples = extract_templates_and_params(data, True)
    #     for _template_name, content, _raw_template in template_triples:
    #         gb: GoogleBooks = GoogleBooksSchema().load(content)
    #         gb.wikibase = IASandboxWikibase()
    #         gb.finish_parsing()
    #         console.print(gb.dict())
    #         assert gb.url == "https://books.google.com/books?id=CDJpAAAAMAAJ"
    #
    # def test_id_with_too_many_chars(self):
    #     data = "{{google books |plainurl=y |id=CDJpAAAAMAAJTEST |page=313d}}"
    #     template_triples = extract_templates_and_params(data, True)
    #     for _template_name, content, _raw_template in template_triples:
    #         GoogleBooksSchema().load(content)
    #
    # def test_id_with_too_few_chars(self):
    #     data = "{{google books |plainurl=y |id=CDJpAAAAMAA |page=313d}}"
    #     template_triples = extract_templates_and_params(data, True)
    #     for _template_name, content, _raw_template in template_triples:
    #         GoogleBooksSchema().load(content)
