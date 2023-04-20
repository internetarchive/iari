from collections import OrderedDict
from unittest import TestCase

from test_data.test_content import (  # type: ignore
    easter_island_tail_excerpt,
    easter_island_head_excerpt,
    sncaso_tail_excerpt
)

from src.models.mediawiki.section import MediawikiSection
from src.models.wikimedia.wikipedia.reference.template.template import WikipediaTemplate


class TestMediawikiSection(TestCase):

    def test_name(self):
        section = MediawikiSection(
            testing=True,
            wikicode=sncaso_tail_excerpt,
        )
        assert section.name == "External links"

    def test_star_found_at_line_start(self):
        section = MediawikiSection(
            testing=True,
            wikicode=sncaso_tail_excerpt,
        )
        lines = str(section.wikicode).split("\n")
        assert section.star_found_at_line_start(line=lines[1]) is False
        assert section.star_found_at_line_start(line=lines[2]) is True

    def test_extract(self):
        section = MediawikiSection(
            testing=True,
            wikicode=sncaso_tail_excerpt,
        )
        section.extract()
        assert section.number_of_references == 1
        ref = section.references[0]
        assert ref.templates == list()
        assert ref.reference_id == "ab202d2e"

    def test_extract_all_general_references__(self):
        section = MediawikiSection(
            testing=True,
            wikicode=sncaso_tail_excerpt,
        )
        section.__extract_all_general_references__()
        print(section.references)
        assert section.number_of_references == 1
        ref = section.references[0]
        assert ref.templates == list()
        assert ref.reference_id == "ab202d2e"

    def test_extract_all_footnote_references__(self):
        section2 = MediawikiSection(wikicode=easter_island_head_excerpt, testing=True)
        section2.__extract_all_footnote_references__()
        assert section2.number_of_references == 3
        ref = section2.references[0]
        assert ref.templates == [
            WikipediaTemplate(
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
                raw_template="{{cite web | url= http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php | title= Censo de Población y Vivienda 2002 | work= [[National Statistics Institute (Chile)|National Statistics Institute]] | access-date= 1 May 2010 | url-status=live | archive-url= https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php | archive-date= 15 July 2010}}",
                extraction_done=True,
                missing_or_empty_first_parameter=False,
                isbn="",
            )
        ]
        assert ref.reference_id == "b64ae445"
