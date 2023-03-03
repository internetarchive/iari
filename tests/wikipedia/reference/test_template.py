from mwparserfromhell import parse  # type: ignore

from src.models.wikimedia.wikipedia.reference.template import WikipediaTemplate
from src.models.wikimedia.wikipedia.url import WikipediaUrl


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

    # def test_found_multiref_template_false(self):
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
    #     templates = parse(data).ifilter_templates()
    #     for template in templates:
    #         wt = WikipediaTemplate(raw_template=template)
    #         wt.extract_and_prepare_parameter_and_flds()
    #         # print(wt.parameters)
    #         assert wt.name == "cite web"
    #         assert wt.is_known_multiref_template is False
    #         assert wt.is_cs1_template is True
    #
    # def test_number_of_templates_missing_first_parameter_zero(self):
    #     data = (
    #         "<ref>{{url|1=https://books.google.com/books?id=28tmAAAAMAAJ&pg=PR7 <!--|alternate-full-text-url="
    #         "https://babel.hathitrust.org/cgi/pt?id=mdp.39015027915100&view=1up&seq=11 -->}}</ref>"
    #     )
    #     templates = parse(data).ifilter_templates()
    #     for template in templates:
    #         wt = WikipediaTemplate(raw_template=template)
    #         wt.extract_and_prepare_parameter_and_flds()
    #         # print(wt.parameters)
    #         assert wt.missing_or_empty_first_parameter is False
    #
    # def test_number_of_templates_missing_first_parameter_one(self):
    #     data = "<ref>{{url|}}</ref>"
    #     templates = parse(data).ifilter_templates()
    #     for template in templates:
    #         wt = WikipediaTemplate(raw_template=template)
    #         wt.extract_and_prepare_parameter_and_flds()
    #         # print(wt.parameters)
    #         assert wt.name == "url"
    #         assert wt.__first_parameter__ == ""
    #         assert wt.missing_or_empty_first_parameter is True
    #
    # def test_get_isbn(self):
    #     wikitext = (
    #         "<ref>{{cite book |last1=Griehl |first1=Manfred |last2="
    #         "Dressel |first2=Joachim |title=Heinkel He 177 - 277 - 274 |year"
    #         "=1998 |publisher=Airlife Publishing |"
    #         "location=Shrewsbury, UK |isbn=1-85310-364-0 |pages=208–209 }}</ref>"
    #     )
    #     templates = parse(wikitext).ifilter_templates()
    #     for template in templates:
    #         wt = WikipediaTemplate(raw_template=template)
    #         wt.extract_and_prepare_parameter_and_flds()
    #         # print(wt.parameters)
    #         assert wt.get_isbn == "1-85310-364-0"
    #
    # def test_get_doi(self):
    #     wikitext = (
    #         "<ref>{{cite journal |author=Peiser, B. |"
    #         "url=http://www.uri.edu/artsci/ecn/starkey/ECN398%20-Ecology,%20Economy,%20Society/RAPANUI."
    #         "pdf |archive-url=https://web.archive.org/web/20100610062402/http://www"
    #         ".uri.edu/artsci/ecn/starkey/ECN398%20-Ecology,%20Economy,%20Society/RAPANUI.pdf |url"
    #         "-status=dead |archive-date=2010-06-10 |title=From Genocide to Ecocide: The Rape of Rapa "
    #         "Nui |doi=10.1260/0958305054672385 |journal=Energy & Environment |volume=16 |issue=3&4 |pages"
    #         "=513–539 |year=2005 |citeseerx=10.1.1.611.1103 |s2cid=155079232 }}</ref>"
    #     )
    #     templates = parse(wikitext).ifilter_templates()
    #     for template in templates:
    #         wt = WikipediaTemplate(raw_template=template)
    #         wt.extract_and_prepare_parameter_and_flds()
    #         # print(wt.parameters)
    #         assert wt.get_doi == "10.1260/0958305054672385"

    # def test_doi_extraction(self):
    #     wikitext = (
    #         "<ref>{{cite journal |author=Peiser, B. |"
    #         "url=http://www.uri.edu/artsci/ecn/starkey/ECN398%20-Ecology,%20Economy,%20Society/RAPANUI."
    #         "pdf |archive-url=https://web.archive.org/web/20100610062402/http://www"
    #         ".uri.edu/artsci/ecn/starkey/ECN398%20-Ecology,%20Economy,%20Society/RAPANUI.pdf |url"
    #         "-status=dead |archive-date=2010-06-10 |title=From Genocide to Ecocide: The Rape of Rapa "
    #         "Nui |doi=10.1260/0958305054672385 |journal=Energy & Environment |volume=16 |issue=3&4 |pages"
    #         "=513–539 |year=2005 |citeseerx=10.1.1.611.1103 |s2cid=155079232 }}</ref>"
    #     )
    #     templates = parse(wikitext).ifilter_templates()
    #     for template in templates:
    #         wt = WikipediaTemplate(raw_template=template)
    #         wt.extract_and_prepare_parameter_and_flds()
    #         # print(wt.parameters)
    #         assert wt.doi_lookup_done is True
    #         console.print(wt.doi)
    #         assert wt.doi == Doi(doi="10.1260/0958305054672385")
    #
    # def test___extract_and_lookup_doi__(self):
    #     wikitext = (
    #         "<ref>{{cite journal |author=Peiser, B. |"
    #         "url=http://www.uri.edu/artsci/ecn/starkey/ECN398%20-Ecology,%20Economy,%20Society/RAPANUI."
    #         "pdf |archive-url=https://web.archive.org/web/20100610062402/http://www"
    #         ".uri.edu/artsci/ecn/starkey/ECN398%20-Ecology,%20Economy,%20Society/RAPANUI.pdf |url"
    #         "-status=dead |archive-date=2010-06-10 |title=From Genocide to Ecocide: The Rape of Rapa "
    #         "Nui |doi=10.1260/0958305054672385 |journal=Energy & Environment |volume=16 |issue=3&4 |pages"
    #         "=513–539 |year=2005 |citeseerx=10.1.1.611.1103 |s2cid=155079232 }}</ref>"
    #     )
    #     templates = parse(wikitext).ifilter_templates()
    #     for template in templates:
    #         wt = WikipediaTemplate(raw_template=template)
    #         wt.__extract_and_clean_template_parameters__()
    #         wt.__extract_and_lookup_doi__()
    #         console.print(wt.doi)
    #         assert wt.doi_lookup_done is True
    #         console.print(wt.doi)
    #         assert wt.doi.doi == "10.1260/0958305054672385"
    #         assert wt.doi.marked_as_retracted_in_openalex is False
    #         assert wt.doi.marked_as_retracted_in_wikidata is False
    #         assert wt.doi.found_in_wikidata is True
    #         assert wt.doi.found_in_openalex is True
