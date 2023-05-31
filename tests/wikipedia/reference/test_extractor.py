import sys
from unittest import TestCase

from src.helpers.console import console
from src.models.api.job.article_job import ArticleJob
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.reference.extractor import (
    WikipediaReferenceExtractor,
)
from test_data.test_content import (  # type: ignore
    easter_island_head_excerpt,
    easter_island_tail_excerpt,
    electrical_breakdown_full_article,
    old_norse_sources,
    test_full_article,
)

# wikibase = IASandboxWikibase()


class TestWikipediaReferenceExtractor(TestCase):
    job = None

    def setUp(self) -> None:
        job = ArticleJob(
            regex="bibliography|further reading|works cited|sources|Test section"
        )
        job.validate_regex_and_extract_url()
        self.job = job

    def test_number_of_references_zero(self):
        wre0 = WikipediaReferenceExtractor(testing=True, wikitext="", job=self.job)
        with self.assertRaises(MissingInformationError):
            wre0.extract_all_references()

    def test_number_of_references_two(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"==Test section==\n<ref>{raw_template}</ref>"
        raw_template2 = "{{citeq|Q2}}"
        raw_reference2 = f"<ref>{raw_template2}</ref>"
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=raw_reference + raw_reference2, job=self.job
        )
        # print(wre.wikitext)
        wre.extract_all_references()
        assert len(wre.references) == 2

    def test_number_of_references_three(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"==Test section==\n<ref>{raw_template}</ref>"
        raw_template2 = "{{cite web|url=http://google.com}}"
        raw_reference2 = f"<ref>{raw_template2}</ref>"
        raw_template3 = "{{citeq|Q3}}"
        raw_reference3 = f"<ref>{raw_template3}</ref>"
        wre1 = WikipediaReferenceExtractor(
            testing=True,
            wikitext=raw_reference + raw_reference2 + raw_reference3,
            job=self.job,
        )
        # print(wre1.wikitext)
        wre1.extract_all_references()
        assert len(wre1.references) == 3

    # def test_extract_all_references(self):
    #     raw_template = "{{citeq|Q1}}"
    #     raw_reference = f"<ref>{raw_template}</ref>"
    #     wre2 = WikipediaReferenceExtractor(testing=True, wikitext=raw_reference)
    #     wre2.extract_all_references()
    #     assert wre2.number_of_references == 1
    #     assert wre2.references[0].first_parameter == "Q1"

    def test_extract_all_references_named_reference(self):
        raw_template = "{{citeq|Q1}}"
        named_reference = '<ref name="INE"/>'
        raw_reference = f"==Test section==\n<ref>{raw_template}</ref>{named_reference}"
        wre2 = WikipediaReferenceExtractor(
            testing=True, wikitext=raw_reference, job=self.job
        )
        wre2.extract_all_references()
        assert len(wre2.references) == 2
        assert wre2.references[0].templates[0].name == "citeq"
        assert wre2.references[0].templates[0].parameters["first_parameter"] == "Q1"

    # def test_number_of_hashed_content_references(self):
    #     wre = WikipediaReferenceExtractor(
    #         testing=True, wikitext=easter_island_head_excerpt
    #     )
    #     wre.extract_all_references()
    #     assert wre.number_of_references == 3
    #     assert wre.number_of_content_references == 2
    #     assert wre.number_of_empty_named_references == 1
    #     assert wre.number_of_hashed_content_references == 2

    # def test_number_of_references_with_a_supported_template(self):
    #     wre = WikipediaReferenceExtractor(
    #         testing=True, wikitext=easter_island_head_excerpt
    #     )
    #     wre.extract_all_references()
    #     assert wre.number_of_content_references_with_any_supported_template == 2
    #
    # def test_number_of_cs1_references(self):
    #     wre = WikipediaReferenceExtractor(
    #         testing=True, wikitext=easter_island_head_excerpt
    #     )
    #     wre.extract_all_references()
    #     assert wre.number_of_cs1_references == 2

    # def test___extract_all_raw_general_references__(self):
    #     """This tests extraction of sections and references"""
    #     print(self.job)
    #     wre = WikipediaReferenceExtractor(
    #         testing=True, wikitext=easter_island_tail_excerpt, job=self.job
    #     )
    #     wre.__extract_all_raw_general_references__()
    #     assert wre.number_of_sections_found == 3

    def test__extract_raw_templates_two(self):
        raw_template = "{{citeq|Q1}}"
        raw_reference = f"==Test section==\n<ref>{raw_template}</ref>"
        raw_template2 = "{{citeq|Q2}}"
        raw_reference2 = f"<ref>{raw_template2}</ref>"
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=raw_reference + raw_reference2, job=self.job
        )
        # print(wre.wikitext)
        wre.extract_all_references()
        assert wre.number_of_sections == 1
        assert wre.content_references[0].number_of_templates == 1
        assert wre.content_references[1].number_of_templates == 1

    def test__extract_sections_test(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=test_full_article, job=self.job
        )
        wre.__extract_sections__()
        assert wre.number_of_sections == 8

    def test__extract_sections_easter_island(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt, job=self.job
        )
        wre.__extract_sections__()
        assert wre.number_of_sections == 5

    def test_extract_general_references_only(self):
        """This tests extraction of sections and references"""
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt, job=self.job
        )
        wre.extract_all_references()
        assert wre.number_of_sections == 5
        assert wre.number_of_general_references == 22
        assert wre.number_of_footnote_references == 0

    def test_isbn_template(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="==Test section==<\n<ref>{{isbn|1234}}</ref>",
            job=self.job,
        )
        wre.extract_all_references()
        assert wre.content_references[0].templates[0].name == "isbn"
        assert wre.content_references[0].templates[0].isbn == "1234"
        # assert wre.number_of_isbn_template_references == 1
        # assert wre.number_of_hashed_content_references == 1

    def test_first_level_domains_one(self):
        example_reference = (
            "==Test section==\n<ref>{{cite web|url=http://google.com}}</ref>"
        )
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=example_reference, job=self.job
        )
        wre.extract_all_references()
        assert wre.first_level_domains == ["google.com"]

    def test_first_level_domains_two(self):
        example_reference = (
            "==Test section==\n<ref>{{cite web|url=http://google.com}}</ref>"
        )
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=example_reference + example_reference, job=self.job
        )
        wre.extract_all_references()
        assert wre.first_level_domains == ["google.com", "google.com"]

    def test_first_level_domain_counts_simple(self):
        example_reference = (
            "==Test section==\n<ref>{{cite web|url=http://google.com}}</ref>"
        )
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=example_reference + example_reference, job=self.job
        )
        wre.extract_all_references()
        assert wre.first_level_domain_counts == {"google.com": 2}

    def test_first_level_domain_counts_excerpt(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt, job=self.job
        )
        wre.extract_all_references()
        assert len(wre.first_level_domains) == 10
        assert len(wre.first_level_domain_counts) == 7
        assert wre.first_level_domain_counts == {
            "archive.org": 4,
            "auckland.ac.nz": 1,
            "bnf.fr": 1,
            "google.com": 1,
            "oclc.org": 1,
            "pisc.org.uk": 1,
            "usatoday.com": 1,
        }

    def test_first_level_domain_counts_excerpt_electrical(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=electrical_breakdown_full_article, job=self.job
        )
        wre.extract_all_references()
        assert len(wre.first_level_domains) == 5
        for fld in [
            "google.com",
            "hypertextbook.com",
            "arcsuppressiontechnologies.com",
            "archive.org",
        ]:
            assert fld in wre.first_level_domains
            assert wre.first_level_domains.count("google.com") == 2
        assert len(wre.first_level_domain_counts) == 4
        assert wre.first_level_domain_counts == {
            "archive.org": 1,
            "arcsuppressiontechnologies.com": 1,
            "google.com": 2,
            "hypertextbook.com": 1,
        }

    def test_first_level_domain_counts_excerpt_oldnorse(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=old_norse_sources, job=self.job
        )
        wre.extract_all_references()
        assert len(wre.urls) == 24
        assert wre.urls[0].dict() == {
            "first_level_domain": "menota.org",
            "fld_is_ip": False,
            "url": "http://www.menota.org/HB2_index.xml",
            "scheme": "http",
            "netloc": "www.menota.org",
            "tld": "org",
            "malformed_url": False,
            "malformed_url_details": None,
            "archived_url": "",
            "wayback_machine_timestamp": "",
            "is_valid": True,
        }
        assert len(wre.raw_urls) == 24
        assert wre.raw_urls == [
            "http://www.menota.org/HB2_index.xml",
            "https://archive.org/details/johnsonsuniversa07adam",
            "https://archive.org/details/bub_gb_RnEJAAAAQAAJ",
            "http://www.germanic-lexicon-project.org/texts/oi_cleasbyvigfusson_about.html",
            "https://old-norse.net",
            "https://archive.org/details/enskslenzkorabk00zogoog",
            "https://archive.org/details/slenzkenskorab00zouoft",
            "http://lexicon.ff.cuni.cz/texts/oi_zoega_about.html",
            "http://norroen.info/dct/zoega/",
            "https://onp.ku.dk/onp/onp.php",
            "https://archive.org/details/lexiconpoticuma00copegoog",
            "http://www.septentrionalia.net/etexts/",
            "https://archive.org/details/elementarygramma00bayluoft",
            "https://archive.org/details/icelandicprosere00guuoft",
            "https://digital-humanities.uni-tuebingen.de/altn-gram/noreen1923.html",
            "https://archive.org/details/altschwedischegr00noreuoft/page/n11/mode/2up",
            "https://digital-humanities.uni-tuebingen.de/altn-gram/haugen2015.html",
            "http://runeberg.org/gutasaga/",
            "http://www.germanicmythology.com/works/Gutasagan.html",
            "https://archive.org/details/introductiontool00gord",
            "https://archive.org/details/icelandicprimerw00swee",
            "http://lexicon.ff.cuni.cz/texts/oi_sweet_about.html",
            "http://www.gutenberg.org/ebooks/5424",
            "https://notendur.hi.is/~haukurth/norse/",
        ]
        assert wre.first_level_domains == [
            "menota.org",
            "archive.org",
            "archive.org",
            "germanic-lexicon-project.org",
            "old-norse.net",
            "archive.org",
            "archive.org",
            "cuni.cz",
            "norroen.info",
            "ku.dk",
            "archive.org",
            "septentrionalia.net",
            "archive.org",
            "archive.org",
            "uni-tuebingen.de",
            "archive.org",
            "uni-tuebingen.de",
            "runeberg.org",
            "germanicmythology.com",
            "archive.org",
            "archive.org",
            "cuni.cz",
            "gutenberg.org",
            "hi.is",
        ]
        assert len(wre.first_level_domains) == 24
        assert len(wre.first_level_domain_counts) == 13
        assert wre.first_level_domain_counts == {
            "archive.org": 10,
            "uni-tuebingen.de": 2,
            "cuni.cz": 2,
            "norroen.info": 1,
            "hi.is": 1,
            "menota.org": 1,
            "germanicmythology.com": 1,
            "runeberg.org": 1,
            "old-norse.net": 1,
            "gutenberg.org": 1,
            "germanic-lexicon-project.org": 1,
            "ku.dk": 1,
            "septentrionalia.net": 1,
        }

    def test___get_checked_and_unique_reference_urls__(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="==Test section==\n<ref>{{cite web|url=http://google.com}}</ref>",
            job=self.job,
        )
        wre.extract_all_references()
        assert len(wre.references) == 1
        assert len(wre.urls) == 1

    def test_reference_urls(self):
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext="==Test section==\n<ref>{{cite web|url=http://google.com}}</ref>",
            job=self.job,
        )
        wre.extract_all_references()
        assert len(wre.urls) == 1
        for url in wre.urls:
            assert url.url == "http://google.com"
            assert url.first_level_domain == "google.com"

    def test_sections_sources(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=old_norse_sources, job=self.job
        )
        wre.extract_all_references()
        assert wre.number_of_sections == 2
        assert wre.number_of_general_references == 42

    def test_sections_no_general_references(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=electrical_breakdown_full_article, job=self.job
        )
        wre.extract_all_references()
        assert wre.number_of_sections == 8
        assert wre.number_of_general_references == 0

    def test_sections_easter_island_tail(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt, job=self.job
        )
        wre.extract_all_references()
        assert wre.number_of_sections == 5

    def test_root_section_easter_island_head(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_head_excerpt, job=self.job
        )
        wre.extract_all_references()
        assert wre.number_of_sections == 1
        assert wre.sections[0].name == "root"

    def test_parameters_easter_island_tail(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=easter_island_tail_excerpt, job=self.job
        )
        wre.extract_all_references()
        assert wre.number_of_sections == 5
        assert wre.number_of_general_references == 22
        for reference in wre.references:
            if reference.template_names and not reference.get_template_dicts:
                console.print(reference)
                sys.exit()

    def test_parameters_yardbirds_reference(self):
        """This should result in 1 footnote reference and 0 general references
        We check that all templates have parameters also"""
        wre = WikipediaReferenceExtractor(
            testing=True,
            wikitext=(
                "==Not a general reference section==\n"
                "<ref>The following sources refer to the Yardbirds as blues rock:\n"
                "*{{cite book |last= Knowles|first= Christopher|date= 2010|title"
                "= The Secret History of Rock 'n' Roll|url= https://"
                "books.google.com/books?id=TMHr1g7T8gQC&q=The+Yardbirds+blues+rock"
                "&pg=PT93|publisher= Viva Editions|isbn= 978-1573444057}}\n*{{"
                "cite book|last= Talevski|first= Nick|date= 1999|title= The Encyclopedia of Rock Obituaries"
                "|url= https://archive.org/details/tombstoneblues00nick/page/356|publisher= Omnibus Press"
                "|page= [https://archive.org/details/tombstoneblues00nick/page/"
                "356 356]|isbn= 978-0711975484}}\n*{{cite book|last= Witmer|first= Scott|"
                "date= 2009|title= History of Rock Bands|url= https://archive.org/details/"
                "historyofrockban0000witm/page/18|publisher= Abdo Publishing Company|page= [https://archive"
                ".org/details/historyofrockban0000witm/page/18 18]|isbn= 978-1604536928}}\n"
                "*{{cite book |last= Wadhams|first= Wayne|date= 2001|title= Inside the Hits: The Seduction of"
                " a Rock and Roll Generation (Pop Culture)|publisher= Omnibus Press|page= 189|"
                "isbn= 978-0634014307}}</ref>"
            ),
            job=self.job,
        )
        wre.extract_all_references()
        assert wre.number_of_sections == 1
        section = wre.sections[0]
        assert section.is_general_reference_section is False
        assert section.name == "Not a general reference section"
        assert len(wre.references) == 1
        first_reference = wre.references[0]
        assert first_reference.section == "Not a general reference section"
        assert first_reference.is_footnote_reference is True
        assert first_reference.number_of_templates == 4
        # check if all templates have parameters
        for template in first_reference.templates:
            if not template.parameters:
                console.print(template)
                raise MissingInformationError()

    def test___extract_root_section__(self):
        wre = WikipediaReferenceExtractor(
            testing=True, wikitext=electrical_breakdown_full_article, job=self.job
        )
        wre.__parse_wikitext__()
        wre.__extract_root_section__()
        assert wre.number_of_sections == 1
        assert wre.sections[0].name == "root"
