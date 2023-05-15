from collections import OrderedDict
from unittest import TestCase

from mwparserfromhell.nodes import Template  # type: ignore

from src.v2.models.api.job.article_job import ArticleJob
from src.v2.models.mediawiki.section import MediawikiSection
from src.v2.models.wikimedia.wikipedia.reference.template.template import (
    WikipediaTemplate,
)
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    easter_island_tail_excerpt,
    sncaso_tail_excerpt,
)


class TestMediawikiSection(TestCase):
    regex_job = ArticleJob(
        regex="bibliography|further reading|works cited|sources|external links"
    )

    def test_name(self):
        section = MediawikiSection(
            testing=True, wikitext=sncaso_tail_excerpt, job=self.regex_job
        )
        assert section.name == "External links"

    def test_star_found_at_line_start(self):
        section = MediawikiSection(
            testing=True, wikitext=sncaso_tail_excerpt, job=self.regex_job
        )
        lines = section.__get_lines__
        assert section.star_found_at_line_start(line=lines[1]) is False
        assert section.star_found_at_line_start(line=lines[2]) is True

    def test_extract(self):
        section = MediawikiSection(
            testing=True, wikitext=sncaso_tail_excerpt, job=self.regex_job
        )
        section.extract()
        assert section.number_of_references == 1
        ref = section.references[0]
        assert ref.templates == list()
        assert ref.reference_id == "ab202d2e"

    def test_extract_all_general_references__(self):
        section = MediawikiSection(
            testing=True, wikitext=sncaso_tail_excerpt, job=self.regex_job
        )
        section.extract()
        print(section.references)
        assert section.number_of_references == 1
        ref = section.references[0]
        assert ref.templates == list()
        assert ref.reference_id == "ab202d2e"

    def test_extract_all_footnote_references__(self):
        section2 = MediawikiSection(
            wikitext=easter_island_head_excerpt, testing=True, job=self.regex_job
        )
        section2.extract()
        assert section2.number_of_references == 3
        ref = section2.references[0]
        assert ref.reference_id == "b64ae445"
        first_template = ref.templates[0]
        first_template.raw_template = Template(name="test")
        assert first_template == WikipediaTemplate(
            raw_template=Template(name="test"),
            parameters=OrderedDict(
                [
                    (
                        "url",
                        "http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
                    ),
                    ("title", "Censo de Población y Vivienda 2002"),
                    (
                        "work",
                        "[[National Statistics Institute (Chile)|National Statistics Institute]]",
                    ),
                    ("access_date", "1 May 2010"),
                    ("url_status", "live"),
                    (
                        "archive_url",
                        "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
                    ),
                    ("archive_date", "15 July 2010"),
                    ("template_name", "cite web"),
                ]
            ),
            extraction_done=True,
            missing_or_empty_first_parameter=False,
            isbn="",
        )

    def test_is_general_reference_section_true(self):
        section = MediawikiSection(
            testing=True, wikitext=sncaso_tail_excerpt, job=self.regex_job
        )
        assert section.name == "External links"
        assert section.is_general_reference_section is True

    def test_is_general_reference_section_false(self):
        section = MediawikiSection(
            testing=True, wikitext="==Test==", job=self.regex_job
        )
        assert section.name == "Test"
        assert section.is_general_reference_section is False
