from collections import OrderedDict

from mwparserfromhell import parse  # type: ignore

from src.v2.models.wikimedia.wikipedia.reference.template.template import (
    WikipediaTemplate,
)
from src.v2.models.wikimedia.wikipedia.url import WikipediaUrl


class TestTemplate:
    def test__remove_comments__(self):
        data = "{{test}}"
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            assert wt.__remove_comments__(text="test<!--test-->") == "test"

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
            wt.extract_and_prepare_parameter_and_flds()
            assert wt.parameters["foo"] == "bar"

    def test_extract_and_prepare_parameters_citeq(self):
        data = "{{citeq|Q1}}"
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            wt.extract_and_prepare_parameter_and_flds()
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
            wt.extract_and_prepare_parameter_and_flds()
            assert (
                wt.parameters["1"]
                == "https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7"
            )

    def test_cite_web_from_easter_island(self):
        """Test on templates from the wild"""
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
            wt.extract_and_prepare_parameter_and_flds()
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
            wt.extract_and_prepare_parameter_and_flds()
            # print(wt.parameters)
            assert wt.name == "citeq"
            assert wt.parameters["first_parameter"] == "Q1"

    # def test_urls(self):
    #     """Test on templates from the wild"""
    #     data = (
    #         '<ref name="INE">{{cite web '
    #         "| url= http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php |"
    #         " title= Censo de Población y Vivienda 2002 | work= [[National Statistics Institute (Chile)|National "
    #         "Statistics Institute]] | access-date= 1 May 2010 | url-status=live "
    #         "| archive-url= https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/"
    #         "censos_poblacion_vivienda/censo_pobl_vivi.php | archive-date= 15 July 2010}}</ref>"
    #     )
    #     templates = parse(data).ifilter_templates()
    #     for templates in templates:
    #         wt = WikipediaTemplate(raw_template=templates)
    #         wt.extract_and_prepare_parameters()
    #         assert wt.urls == {
    #             "http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
    #             "https://web.archive.org/web/20100715195638/http://"
    #             "www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
    #         }

    def test_urls(self):
        """Test on templates from the wild"""
        data = (
            '<ref name="INE">{{cite web '
            "| url= http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php "
            "| chapter-url= http://www.test1.com"
            "| conference-url= http://www.test2.com"
            "| transcript-url= http://www.test3.com"
            "|"
            " title= Censo de Población y Vivienda 2002 | work= [[National Statistics Institute (Chile)|National "
            "Statistics Institute]] | access-date= 1 May 2010 | url-status=live "
            "| archive-url= https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/"
            "censos_poblacion_vivienda/censo_pobl_vivi.php | archive-date= 15 July 2010}}</ref>"
        )
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            wt.extract_and_prepare_parameter_and_flds()
            assert (
                WikipediaUrl(
                    soft404_probability=0.0,
                    url="http://www.test1.com",
                    checked=False,
                    status_code=0,
                    first_level_domain="",
                )
                in wt.urls
            )
            assert (
                WikipediaUrl(
                    soft404_probability=0.0,
                    url="http://www.test3.com",
                    checked=False,
                    status_code=0,
                    first_level_domain="",
                )
                in wt.urls
            )
            assert (
                WikipediaUrl(
                    soft404_probability=0.0,
                    url="http://www.test2.com",
                    checked=False,
                    status_code=0,
                    first_level_domain="",
                )
                in wt.urls
            )
            assert (
                WikipediaUrl(
                    soft404_probability=0.0,
                    url="https://web.archive.org/web/20100715195638/"
                    "http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
                    checked=False,
                    status_code=0,
                    first_level_domain="",
                )
                in wt.urls
            )
            assert (
                WikipediaUrl(
                    soft404_probability=0.0,
                    url="http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
                    checked=False,
                    status_code=0,
                    first_level_domain="",
                )
                in wt.urls
            )

    def test_extract_isbn_from_cite_book_template(self):
        """Using real template from https://en.wikipedia.org/wiki/Bicycle"""
        data = (
            '<ref name="Wilson">{{cite book | title = Bicycling Science | '
            "url = https://archive.org/details/isbn_9780262731546 | url-access = "
            "registration | edition = Third | last = Wilson | first = David Gordon |"
            "author2=Jim Papadopoulos | year = 2004 | publisher = The MIT Press | "
            "isbn = 978-0-262-73154-6 | pages = "
            "[https://archive.org/details/isbn_9780262731546/page/270 270–72]}}</ref>"
        )
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            wt.extract_and_prepare_parameter_and_flds()
            assert wt.isbn == "978-0-262-73154-6"
            assert wt.get_dict() == {
                "isbn": "978-0-262-73154-6",
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
                            "[https://archive.org/details/isbn_9780262731546/page/270 "
                            "270–72]",
                        ),
                        ("template_name", "cite book"),
                    ]
                ),
            }
            # print(wt.parameters)

    def test_extract_isbn_from_isbn_template(self):
        """This template is made up"""
        data = '<ref name="Wilson">{{isbn|978-0-262-73154-6}}</ref>'
        templates = parse(data).ifilter_templates()
        for template in templates:
            wt = WikipediaTemplate(raw_template=template)
            wt.extract_and_prepare_parameter_and_flds()
            assert wt.isbn == "978-0-262-73154-6"
