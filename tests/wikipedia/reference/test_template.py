from mwparserfromhell import parse  # type: ignore

from src.models.wikimedia.wikipedia.reference.template import WikipediaTemplate


class TestTemplate:
    def test__remove_comments__(self):
        data = "{{test}}"
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            assert "test" == wt.__remove_comments__(text="test<!--test-->")

    def test_name(self):
        data = "{{test}}"
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            assert wt.name == "test"

    def test_extract_and_prepare_parameters(self):
        data = "{{test|foo=bar}}"
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            wt.extract_and_prepare_parameters()
            assert wt.parameters["foo"] == "bar"

    def test_raw_template_url(self):
        data = (
            "{{url|1=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 <!--|alternate-full-text-url="
            "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 -->}}"
        )
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            wt.extract_and_prepare_parameters()
            assert (
                wt.parameters["1"]
                == "https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7"
            )

        # assert (
        #     wrr.templates[0].raw_template
        #     == data
        # )
        # content["template_name"] = name
        # reference = EnglishWikipediaReference(**content)
        # reference.raw_template = raw
        # reference.wikibase = IASandboxWikibase()
        # reference.finish_parsing_and_generate_hash(testing=True)
        # # we test that it is still correct
        # assert wrr.raw_template == raw
