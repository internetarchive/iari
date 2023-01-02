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
        data = "{{citeq|Q1}}"
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            assert wt.name == "citeq"

    def test_extract_and_prepare_parameters(self):
        data = "{{test|foo=bar}}"
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            wt.extract_and_prepare_parameters()
            assert wt.parameters["foo"] == "bar"

    def test_extract_and_prepare_parameters_citeq(self):
        data = "{{citeq|Q1}}"
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            wt.extract_and_prepare_parameters()
            assert wt.parameters["1"] == "Q1"
            assert wt.parameters["first_parameter"] == "Q1"

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

    def test_cite_web_from_easter_island(self):
        """Test on template from the wild"""
        data = (
            '<ref name="INE">{{cite web '
            "| url= http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php |"
            " title= Censo de Población y Vivienda 2002 | work= [[National Statistics Institute (Chile)|National "
            "Statistics Institute]] | access-date= 1 May 2010 | url-status=live "
            "| archive-url= https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/"
            "censos_poblacion_vivienda/censo_pobl_vivi.php | archive-date= 15 July 2010}}</ref>"
        )
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            wt.extract_and_prepare_parameters()
            # print(wt.parameters)
            assert wt.name == "cite web"
            assert wt.parameters["title"] == "Censo de Población y Vivienda 2002"
            assert wt.parameters["url"] == (
                "http://www.ine.cl/canales/chile_estadistico/censos_poblacion_"
                "vivienda/censo_pobl_vivi.php"
            )
            assert wt.parameters["archive_url"] == (
                "https://web.archive.org/web/20100715195638/http://www.ine.cl/c"
                "anales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_"
                "vivi.php"
            )

    def test_citeq_template(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"<ref>{raw_template}</ref>"
        templates = parse(raw_reference).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            wt.extract_and_prepare_parameters()
            # print(wt.parameters)
            assert wt.name == "citeq"
            assert wt.parameters["first_parameter"] == "Q1"
