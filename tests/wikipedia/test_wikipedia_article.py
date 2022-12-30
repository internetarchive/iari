import logging
from unittest import TestCase

from wikibaseintegrator import WikibaseIntegrator  # type: ignore

import config
from src.helpers.console import console
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.enums import WikimediaSite

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestWikipediaArticle(TestCase):
    def test_fix_dash(self):
        # TODO improve this test and document it, it does not make sense
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            wikibase=IASandboxWikibase(),
            language_code="en",
            wikimedia_site=WikimediaSite.WIKIPEDIA,
            title="Easter Island",
        )
        # This uses internet which is not optimal
        page.__get_wikipedia_article_from_title__()
        page.extract_and_parse_references()
        logger.info(f"{len(page.references)} references found")
        for ref in page.references:
            if config.loglevel == logging.INFO or config.loglevel == logging.DEBUG:
                # console.print(ref.template_name)
                if (
                    ref.url
                    == "http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php"
                ):
                    console.print(ref.url, ref.archive_url)

    def test_fetch_page_data_and_parse_the_wikitext(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            wikibase=IASandboxWikibase(),
            language_code="en",
            wikimedia_site=WikimediaSite.WIKIPEDIA,
            title="Test",
        )
        page.__fetch_page_data__()
        assert page.page_id == 11089416
        assert page.title == "Test"
        assert page.found_in_wikipedia is True

    def test_fetch_page_data_invalid_title(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        page = WikipediaArticle(
            wikibase=IASandboxWikibase(),
            language_code="en",
            wikimedia_site=WikimediaSite.WIKIPEDIA,
            title="Test2",
        )
        page.__fetch_page_data__()
        assert page.found_in_wikipedia is False

    # def test_get_wcdqid_from_hash_via_sparql(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     page = WikipediaArticle(
    #         wikibase=IASandboxWikibase(),
    #         language_code="en",
    #         wikimedia_site=WikimediaSite.WIKIPEDIA,
    #         title="Test",
    #     )
    #     # page.__fetch_page_data__(title="Test")
    #     page.extract_and_parse_and_upload_missing_items_to_wikibase()
    #     wcdqid = page.return_.item_qid
    #     console.print(
    #         f"Waiting {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
    #     )
    #     sleep(config.sparql_sync_waiting_time_in_seconds)
    #     check_wcdqid = page.__get_wcdqid_from_hash_via_sparql__(md5hash=page.md5hash)
    #     print(wcdqid, check_wcdqid)
    #     assert wcdqid == check_wcdqid

    def test_is_redirect(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(title="Easter island", wikibase=IASandboxWikibase())
        wp.__fetch_page_data__()
        assert wp.is_redirect is True
        wp = WikipediaArticle(title="Easter Island", wikibase=IASandboxWikibase())
        wp.__fetch_page_data__()
        assert wp.is_redirect is False

    def test_fetch_wikidata_qid_enwiki(self):
        """Test fetching from enwiki"""
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(title="Easter island", wikibase=IASandboxWikibase())
        wp.__fetch_wikidata_qid__()
        assert wp.wikidata_qid == "Q14452"

    def test_fetch_wikidata_qid_dawiki(self):
        """Test fetching from dawiki"""
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(
            title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
        )
        wp.__fetch_wikidata_qid__()
        assert wp.wikidata_qid == "Q14452"

    # DISABLED because it fails. we disabled the method since 2.1.0-alpha2
    # def test_get_title_from_wikidata(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(wdqid="Q1", wikibase=IASandboxWikibase())
    #     wp.__get_title_from_wikidata__()
    #     assert wp.title == "Universe"

    # def test___count_number_of_supported_templates_found_no_templates(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(
    #         title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
    #     )
    #     with self.assertRaises(MissingInformationError):
    #         wp.__count_number_of_supported_templates_found__()
    #
    # def test___count_number_of_supported_templates_found_with_template(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(
    #         title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
    #     )
    #     wp.wikitext = "{{citeq|1}}"
    #     wp.__extract_templates_from_the_wikitext__()
    #     assert len(wp.template_triples) == 1
    #
    # def test___extract_templates_from_the_wikitext_valid(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(
    #         title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
    #     )
    #     wp.wikitext = "{{citeq|1}}"
    #     wp.__extract_templates_from_the_wikitext__()
    #     assert len(wp.template_triples) == 1
    #
    # def test___extract_templates_from_the_wikitext_no_templates(self):
    #     from src.models.wikimedia.wikipedia.article import WikipediaArticle
    #
    #     wp = WikipediaArticle(
    #         title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
    #     )
    #     wp.wikitext = "{citeq|1}}testtestxxxx{}"
    #     wp.__extract_templates_from_the_wikitext__()
    #     assert len(wp.template_triples) == 0

    def test___extract_and_parse_references_citeq(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(
            title="Påskeøen", wikibase=IASandboxWikibase(), language_code="da"
        )
        wp.wikitext = "<ref>{{citeq|1}}</ref>"
        wp.extract_and_parse_references()
        assert len(wp.extractor.references) == 1
        assert wp.extractor.references[0].raw_reference.templates[0].raw_template == "{{citeq|1}}"
        assert wp.extractor.references[0].first_template_name == "citeq"

    def test___extract_and_parse_references_easter_island_excerpt(self):
        from src.models.wikimedia.wikipedia.article import WikipediaArticle

        wp = WikipediaArticle(title="Easter Island", wikibase=IASandboxWikibase())
        wp.wikitext = """{{short description|Chilean island in the Pacific}}
{{for|the Kris Kristofferson album|Easter Island (album)}}
{{Redirect|Rapa Nui}}
{{pp-semi-indef}}
{{Cleanup lang |date=April 2022 }}
{{Use dmy dates |date=October 2020 }}
{{Infobox settlement
<!-- See Template:Infobox settlement for additional fields and descriptions -->
| name                    = Easter Island
| native_name             = {{native name|rap|Rapa Nui}}
| other_name              = {{native name|es|Isla de Pascua}}
| settlement_type         = Special Territory, [[Provinces of Chile|Province]] and [[Communes of Chile|Commune]]
| image_skyline           = Rano Raraku quarry.jpg
| imagesize               =
| image_alt               =
| image_caption           =
| image                   =
| image_flag              = Flag of Rapa Nui, Chile.svg
| flag_size               =
| flag_alt                =
| flag_link               =
| image_seal              = Logotipo de la Gobernación de Isla de Pascua.svg
| image_shield            = Emblem of Easter Island.svg
| shield_size             =
| shield_alt              = Emblem
| shield_link             =
| image_blank_emblem      =
| nickname                =
| motto                   =
| anthem                  =
| image_map               = Easter Island map-en.svg
| mapsize                 =
| map_alt                 =
| map_caption             = Easter Island map showing [[Terevaka]], [[Poike]], [[Rano Kau]], [[Motu Nui]], [[Orongo]], and [[Mataveri International Airport|Mataveri]]; major ahus are marked with [[moai]]
| image_map1              =
| mapsize1                =
| map_alt1                =
| map_caption1            =
| image_dot_map           =
| pushpin_map             = Pacific Ocean
| pushpin_label_position  = <!-- position of the pushpin label: left, right, top, bottom, none -->
| pushpin_label           =
| pushpin_map_alt         =
| pushpin_mapsize         = <!--omit "px"-->
| pushpin_map_caption     =  Easter Island in the Pacific Ocean
| pushpin_map1            =
| pushpin_label_position1 =
| pushpin_label1          =
| pushpin_map_alt1        =
| pushpin_mapsize1        =
| pushpin_map_caption1    =
| pushpin_relief          = 1
| coordinates             = {{coord|27|7|S|109|22|W|region:CL-VL_type:isle_dim:50000|format=dms|display=inline}}
| coor_pinpoint           = <!-- to specify exact location of coordinates (was coor_type) -->
| coordinates_footnotes   =
<!-- location ------------------>
| subdivision_type        = Country
| subdivision_name        = [[Chile]]
| subdivision_type1       = [[Regions of Chile|Region]]
| subdivision_name1       = [[Valparaíso Region|Valparaíso]]
| subdivision_type2       = [[Provinces of Chile|Province]]
| subdivision_name2       = [[Isla de Pascua Province|Isla de Pascua]]
| subdivision_type3       = [[Communes of Chile|Commune]]
| subdivision_name3       = [[Isla de Pascua (commune)|Isla de Pascua]]
<!-- established --------------->
| established_title       =
| established_date        =
| established_title1      =
| established_date1       =
| established_title2      =
| established_date2       =
| established_title3      = Special territory status
| established_date3       =
| founder                 =
| named_for               =
<!-- seat, smaller parts ------->
| seat_type               =
| seat                    = [[Hanga Roa]]
| parts_type              = <!-- defaults to: Boroughs -->
| parts_style             = <!-- list, coll (collapsed list), para (paragraph format) -->
| parts                   = <!-- parts text, or header for parts list -->
| p1                      =
| p2                      = <!-- etc., up to p50: for separate parts to be listed-->
<!-- government type, leaders -->
| government_footnotes    =
| government_type         = Municipality
| governing_body          = [[Municipal council]]
| leader_party            = [[Independent (politician)|IND]]
| leader_title            = Provincial Governor
| leader_name             = [[Laura Alarcón Rapu]]
| leader_title1           = [[Alcalde]]
| leader_name1            = [[Pedro Edmunds Paoa]] ([[Progressive Party (Chile)|PRO]])
| total_type              = <!-- to set a non-standard label for total area and population rows -->
| unit_pref               = Metric
| area_footnotes          =<ref name="INE">{{cite web | url= http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php | title= Censo de Población y Vivienda 2002 | work= [[National Statistics Institute (Chile)|National Statistics Institute]] | access-date= 1 May 2010 | url-status=live | archive-url= https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php | archive-date= 15 July 2010}}</ref>
| area_magnitude          = <!-- use only to set a special wikilink -->
| area_total_km2          = 163.6
| area_rank               =
<!-- elevation ----------------->
| elevation_footnotes     =
| elevation_m             =
| elevation_ft            =
| elevation_max_footnotes =
| elevation_max_m         = 507
| elevation_max_ft        = 1,663
| elevation_min_footnotes =
| elevation_min_m         = 0
| elevation_min_ft        = 0
<!-- population ---------------->
| population_footnotes    =
| population_total        = 7750<ref>{{cite web |language= es |url= https://resultados.censo2017.cl/Home/Download |title= Censo 2017 |work= [[National Statistics Institute (Chile)|National Statistics Institute]] |access-date= 11 May 2018 |archive-url= https://web.archive.org/web/20180511145942/https://resultados.censo2017.cl/Home/Download |archive-date= 11 May 2018 |url-status=dead }}</ref>
| population_as_of        = 2017 census
| population_rank         =
| population_density_km2  = 47
| population_blank1_title = Urban
| population_blank1       = <!--5,563<ref name="2012census">{{cite web|url=http://www.censo.cl/cuadros/Region_5/Poblacion/Cuadro%201.2.xlsx|title=Resultados Censo de Población y Vivienda 2012|publisher=Instituto Nacional de Estadísticas|date=2 April 2013|language=es}}</ref>-->
| population_blank2_title = Rural
| population_blank2       = <!--198<ref name="2012census"/>-->
| population_demonym      = <!-- demonym, ie. Liverpudlian for someone from Liverpool -->
| population_note         =
| demographics_type1      =
| demographics1_footnotes =<ref name="INE"/>
| demographics1_title1    =
| demographics1_info1     =
| demographics1_title2    =
| demographics1_info2     =
| timezone = [[Time in Chile|EAST]]
| utc_offset = −6
| timezone_DST = [[Time in Chile|EASST]]
| utc_offset_DST = −5
<!-- postal codes, area code --->
| postal_code_type        = <!-- enter ZIP code, Postcode, Post code, Postal code... -->
| postal_code             =
| postal2_code_type       = <!-- enter ZIP code, Postcode, Post code, Postal code... -->
| postal2_code            =
| area_code_type          = [[List of country calling codes|Country Code]]
| area_code               = [[+56]]
| geocode                 =
| registration_plate      =
| blank_name_sec1         = Currency
| blank_info_sec1         = [[Chilean Peso|Peso]] ([[ISO 4217|CLP]])
| blank1_name_sec1        = [[Language]]
| blank1_info_sec1        = Spanish, [[Rapa Nui language|Rapa Nui]]
| blank2_name_sec1   = Driving side
| blank2_info_sec1        = right
| blank_name_sec2       =
| blank_info_sec2         =
| blank1_name_sec2        =
| blank1_info_sec2        =
| blank2_name_sec2        =
| blank2_info_sec2        =
| website                 = {{Official URL}}
| footnotes               = [[National Geospatial-Intelligence Agency|NGA]] UFI=-905269
}}
{{Infobox UNESCO World Heritage Site
|WHS        = [[Rapa Nui National Park]]
|Image      = Moai Rano raraku.jpg
|Caption    = [[Moai]] at [[Rano Raraku]], Easter Island
|Criteria   = Cultural: i, iii, v
|ID         = 715
|Year       = 1995
|Area       = 6,666 ha
}}

'''Easter Island''' ({{lang-rap|Rapa Nui}}; {{lang-es|Isla de Pascua}}) is an island and special territory of [[Chile]] 
in the southeastern [[Pacific Ocean]], at the southeasternmost point of the [[Polynesian Triangle]] in [[Oceania]]. 
The island is most famous for its nearly 1,000 extant monumental statues, called ''[[moai]]'', which were created by 
the early [[Rapa Nui people]]. In 1995, [[UNESCO]] named Easter Island a [[World Heritage Site]], with much of the 
island protected within [[Rapa Nui National Park]].
"""
        wp.extract_and_parse_references()
        assert len(wp.extractor.references) == 3
        #print(wp.extractor.references)
        # print(wp.extractor.references[0].raw_reference.templates)
        assert wp.extractor.references[0].raw_reference.number_of_templates == 1
        assert wp.extractor.references[0].raw_reference.templates[0].raw_template == (
            "{{cite web | url= http://www.ine.cl/canales/chile_estadistico/censos_poblacion_viviend"
            "a/censo_pobl_vivi.php | title= Censo de Población y Vivienda 2002 | work= [[National Stati"
            "stics Institute (Chile)|National Statistics Institute]] | access-date= 1 May 2010 | url-stat"
            "us=live | archive-ur"
            "l= https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistic"
            "o/censos_poblacion_vivienda/censo_pobl_vivi.php | archive-date= 15 July 2010}}"
        )
        assert wp.extractor.references[0].first_template_name == "cite web"
        # print(wp.extractor.references[1].raw_reference.templates)
        assert wp.extractor.references[1].raw_reference.templates[0].raw_template == (
            "{{cite web |language= es |url= https://resultados.censo2017.cl/Home/Download |title= Censo 2017 |wo"
            "rk= [[National Statistics Institute (Chile)|National Statistics Institute]] |access-d"
            "ate= 11 May 2018 |archive-url= https://web.archive.org/web/20180511145942/https://resultados.censo2"
            "017.cl/Home/Download |archive-date= 11 May 2018 |url-status=dead }}"
        )
        assert wp.extractor.references[1].first_template_name == "cite web"
        print(wp.extractor.references[2].raw_reference)
        assert wp.extractor.references[2].raw_reference.templates[0].raw_template == (
            "{{cite web |last1=Dangerfield |first1=Whitney |title=The Mystery of Easter Island |url=https://www.sm"
            "ithsonianmag.com/travel/the-mystery-of-easter-island-151285298/ |website=[[Smiths"
            "onian (magazine)|Smithsonian Magazine]] |access-date=December 10, 2020 |date=March 31, 2007}}"
        )
        assert wp.extractor.references[2].first_template_name == "cite web"
        # assert wp.extractor.references[3].raw_reference.templates[0].raw_template == (
        #     "{{cite journal |author=Peiser, B. |url=http://www.uri.edu/artsci/ecn/starkey/ECN398%20-"
        #     "Ecology,%20Economy,%20Society/RAPANUI.pdf |archive-url=https://web.archive.org/web/2010061"
        #     "0062402/http://www.uri.edu/artsci/ecn/starkey/ECN398%20-Ecology,%20Economy,%20Society/RAPANU"
        #     "I.pdf |url-status=dead |archive-date=2010-06-10 |title=From Genocide to Ecocide: "
        #     "The Rape of Rapa Nui |doi=10.1260/0958305054672385 |journal=Energy & Environment |"
        #     "volume=16 |issue=3&4 |pages=513–539 |year=2005 |citeseerx=10.1.1.611.1103 |s2cid=155079232 }}"
        # )
        # assert wp.extractor.references[3].first_template_name == "cite journal"
        # assert wp.extractor.references[4].raw_reference.templates[0].raw_template == (
        #     "{{citation |url=http://www.leychile.cl/Navegar?idNorma=1026285 |title=List of C"
        #     "hilean Provinces |publisher=Congreso Nacional |access-date=20 February 2013 "
        #     "|url-status=live |archive-url=https://web.archive.org/web/20120910034328/http://www"
        #     ".leychile.cl/Navegar?idNorma=1026285 |archive-date=10 September 2012}}"
        # )
        # assert wp.extractor.references[4].first_template_name == "citation"
        # assert wp.extractor.references[5].raw_reference.templates[0].raw_template == (
        #     "{{cite web|url=https://redatam-ine.ine.cl/redbin/RpWebEngine.exe/Portal?BASE=CENSO_2"
        #     "017&lang=esp|title=Instituto Nacional de Estadísticas – REDATAM Procesamiento y disem"
        #     "inación|website=Redatam-ine.ine.cl|access-date=11 January 2019|archive-url=https://web.archi"
        #     "ve.org/web/20190527171611/https://redatam-ine.ine.cl/redbin/RpWebEngine.exe/Portal?B"
        #     "ASE=CENSO_2017&lang=esp|archive-date=27 May 2019|url-status=live}}"
        # )
        # assert wp.extractor.references[5].first_template_name == "cite web"
        # assert wp.extractor.references[6].raw_reference.templates[0].raw_template == (
        #     "{{citation|title=Welcome to Rapa Nui – Isla de Pascua – Easter Island|url=http://www.portal"
        #     "rapanui.cl/rapanui/informaciones.htm|work=Portal RapaNui, the island's official website|url-status=li"
        #     "ve|archive-url=https://web.archive.org/web/20120114041943/http://www.portalrapanui.cl/rapanui/in"
        #     "formaciones.htm|archive-date=14 January 2012}}"
        # )
        # assert wp.extractor.references[6].first_template_name == "citation"
        # assert wp.extractor.references[7].raw_reference.templates[0].raw_template == (
        #     "{{cite web |url=http://www.citypopulation.de/Pitcairn.html |title=Pitcairn Islands |author=Thomas B"
        #     "rinkhoff |date=1 February 2013 |website=Citypopulation.de |publisher=Thomas Brinkhoff |access-d"
        #     "ate=8 November 2013 |url-status=live |archive-url=https://web.archive.org/web/20131015182546/http://w"
        #     "ww.citypopulation.de/Pitcairn.html |archive-date=15 October 2013}}"
        # )
        # assert wp.extractor.references[7].first_template_name == "cite web"
        # assert wp.extractor.references[7].publisher == "Thomas Brinkhoff"
        # assert wp.extractor.references[7].title == "Pitcairn Islands"
        # assert wp.extractor.references[7].url == "http://www.citypopulation.de/Pitcairn.html"
