from collections import OrderedDict
from unittest import TestCase

from mwparserfromhell.wikicode import Wikicode
from test_data.test_content import (  # type: ignore
    easter_island_tail_excerpt,
    easter_island_head_excerpt,
)
from src.models.mediawiki.section import MediawikiSection
from src.models.wikimedia.wikipedia.reference.template.template import WikipediaTemplate


class TestMediawikiSection(TestCase):
    section1 = MediawikiSection(
        testing=True,
        wikicode="""==External links==
{{Commons category|SNCASO}}
* [http://www.aviafrance.com/constructeur.php?ID_CONSTRUCTEUR=1145 SNCASO page] on [http://www.aviafrance.com AviaFrance].

{{SNCASO aircraft}}
{{Sud Aviation}}
{{SNCASO}}
{{Defunct aircraft manufacturers of France}}
{{Authority control}}

{{DEFAULTSORT:Sncaso}}
[[Category:Defunct aircraft manufacturers of France]]
[[Category:Sud Aviation]]
[[Category:Vehicle manufacturing companies established in 1936]]
[[Category:Vehicle manufacturing companies disestablished in 1957]]
[[Category:French companies established in 1936]]
[[Category:1957 disestablishments in France]]
[[Category:Sud-Ouest aircraft| ]] """,
    )

    def test_name(self):
        assert self.section1.name == "External links"

    def test_star_found_at_line_start(self):
        lines = str(self.section1.wikicode).split("\n")
        assert self.section1.star_found_at_line_start(line=lines[1]) is False
        assert self.section1.star_found_at_line_start(line=lines[2]) is True

    def test_extract(self):
        self.section1.extract()
        assert self.section1.number_of_references == 1
        ref = self.section1.references[0]
        assert ref.templates == list()
        assert ref.reference_id == "ab202d2e"

    def test_extract_all_general_references__(self):
        self.section1.__extract_all_general_references__()
        print(self.section1.references)
        assert self.section1.number_of_references == 1
        ref = self.section1.references[0]
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
