from unittest import TestCase

from src.models.identifiers_checking.doi import Doi


class TestDoi(TestCase):
    retracted_in_oa_but_not_wd = "10.1038/nature04695"
    retracted_in_wd_but_not_oa = "10.1126/SCIENCE.1074501"
    retracted_in_both = "10.1186/1824-7288-38-34"
    unretracted_in_either = "10.1136/GUT.52.12.1678"
    unretracted_in_either_lowercase = "10.1136/gut.52.12.1678"

    def test___lookup_doi_in_openalex_not_retracted(self):
        doi = Doi(doi=self.unretracted_in_either)
        doi.__lookup_doi_in_openalex__()
        assert doi.found_in_openalex is True
        assert doi.marked_as_retracted_in_openalex is False
        # assert doi.openalex_work_uri == "https://openalex.org/W2044307156"

    def test___lookup_doi_in_openalex_retracted(self):
        doi = Doi(doi=self.retracted_in_oa_but_not_wd)
        doi.__lookup_doi_in_openalex__()
        assert doi.found_in_openalex is True
        assert doi.marked_as_retracted_in_openalex is True
        # assert doi.openalex_work_uri == "https://openalex.org/W2033363278"

    def test__lookup_via_cirrussearch__1(self):
        doi = Doi(doi=self.retracted_in_wd_but_not_oa)
        doi.__lookup_via_cirrussearch__()
        assert doi.found_in_wikidata is True
        assert doi.wikidata_entity_qid == "Q1964440"

    def test__lookup_via_cirrussearch__2(self):
        doi = Doi(doi=self.retracted_in_both)
        doi.__lookup_via_cirrussearch__()
        assert doi.found_in_wikidata is True
        assert doi.wikidata_entity_qid == "Q21198745"

    def test__lookup_via_cirrussearch__lowercase(self):
        doi = Doi(doi=self.unretracted_in_either_lowercase)
        doi.__lookup_via_cirrussearch__()
        assert doi.found_in_wikidata is True
        assert doi.wikidata_entity_qid == "Q35596193"

    def test___retracted(self):
        doi = Doi(doi=self.retracted_in_wd_but_not_oa)
        doi.__lookup_via_cirrussearch__()
        assert doi.found_in_wikidata is True
        doi.__get_wikidata_entity__()
        doi.__determine_if_retracted_in_wikidata__()
        print(doi.wikidata_entity_uri)
        assert doi.marked_as_retracted_in_wikidata is True

    def test__analyze_wikidata_entity_retracted(self):
        doi = Doi(doi=self.retracted_in_wd_but_not_oa)
        doi.__lookup_via_cirrussearch__()
        assert doi.found_in_wikidata is True
        doi.__analyze_wikidata_entity__()
        print(doi.wikidata_entity_uri)
        assert doi.marked_as_retracted_in_wikidata is True

    def test__analyze_wikidata_entity_unretracted(self):
        doi = Doi(doi=self.retracted_in_oa_but_not_wd)
        doi.__lookup_via_cirrussearch__()
        assert doi.found_in_wikidata is True
        doi.__analyze_wikidata_entity__()
        assert doi.marked_as_retracted_in_wikidata is True

    def test_lookup_doi_unretracted(self):
        doi = Doi(doi=self.unretracted_in_either)
        doi.lookup_doi()
        assert doi.found_in_wikidata is True
        assert doi.found_in_openalex is True
        assert doi.marked_as_retracted_in_wikidata is False
        assert doi.marked_as_retracted_in_openalex is False

    def test_lookup_doi_retracted(self):
        doi = Doi(doi=self.retracted_in_both)
        doi.lookup_doi()
        assert doi.found_in_wikidata is True
        assert doi.found_in_openalex is True
        assert doi.marked_as_retracted_in_wikidata is True
        assert doi.marked_as_retracted_in_openalex is True

    def test_get_cleaned_doi_object(self):
        doi = Doi(doi=self.retracted_in_both)
        doi.lookup_doi()
        dictionary = doi.get_doi_dictionary()
        assert dictionary["doi"] == "10.1186/1824-7288-38-34"

    def test__lookup_in_fatcat__(self):
        doi = Doi(doi=self.retracted_in_both)
        doi.__lookup_in_fatcat__()
        assert doi.fatcat["id"] == "eacv2anmnfbi3dgco4lfxw2utm"
        assert doi.fatcat["details"] == {
            "abstracts": [],
            "refs": [
                {
                    "index": 0,
                    "extra": {"doi": "10.1016/s0022-3999(99)00084-7"},
                    "key": "B2",
                },
                {
                    "index": 1,
                    "extra": {"doi": "10.1111/j.1651-2227.2007.00428.x"},
                    "key": "B6",
                },
                {"index": 2, "extra": {"doi": "10.1136/adc.29.145.165"}, "key": "B8"},
                {"index": 3},
                {
                    "index": 4,
                    "extra": {"doi": "10.1097/00008480-200210000-00005"},
                    "key": "B12",
                },
                {"index": 5, "extra": {"doi": "10.1111/1467-8624.00196"}, "key": "B13"},
                {"index": 6, "extra": {"doi": "10.1542/peds.2004-1036"}, "key": "B15"},
                {
                    "index": 7,
                    "extra": {"doi": "10.1016/s0196-0644(98)70067-8"},
                    "key": "B16",
                },
                {
                    "index": 8,
                    "extra": {"doi": "10.1016/s0031-3955(05)70402-8"},
                    "key": "B17",
                },
                {"index": 9},
                {
                    "index": 10,
                    "extra": {"doi": "10.1016/s0022-3476(85)80260-2"},
                    "key": "B20",
                },
                {"index": 11},
                {
                    "index": 12,
                    "extra": {"doi": "10.1136/bmj.316.7144.1563"},
                    "key": "B23",
                },
                {
                    "index": 13,
                    "extra": {"doi": "10.1097/00005176-200204000-00020"},
                    "key": "B24",
                },
                {
                    "index": 14,
                    "extra": {"doi": "10.1542/peds.106.6.1349"},
                    "key": "B28",
                },
                {
                    "index": 15,
                    "extra": {"doi": "10.1016/s0091-6749(95)70224-5"},
                    "key": "B29",
                },
                {"index": 16, "extra": {"doi": "10.1542/peds.2005-0147"}, "key": "B30"},
                {
                    "index": 17,
                    "extra": {"doi": "10.2500/108854197778594007"},
                    "key": "B31",
                },
                {"index": 18, "extra": {"doi": "10.1136/adc.75.2.141"}, "key": "B32"},
                {"index": 19, "extra": {"doi": "10.1542/peds.2006-1222"}, "key": "B33"},
                {"index": 20, "extra": {"doi": "10.1542/peds.2010-0433"}, "key": "B34"},
                {
                    "index": 21,
                    "extra": {"doi": "10.1111/j.1442-200x.2006.02182.x"},
                    "key": "B36",
                },
                {
                    "index": 22,
                    "extra": {"doi": "10.1016/s0022-3476(05)83557-7"},
                    "key": "B37",
                },
                {"index": 23, "extra": {"doi": "10.1136/adc.84.2.138"}, "key": "B39"},
                {
                    "index": 24,
                    "extra": {"doi": "10.1016/s0161-4754(99)70003-5"},
                    "key": "B40",
                },
                {"index": 25},
                {"index": 26},
                {"index": 27, "extra": {"doi": "10.2307/1127059"}, "key": "B44"},
                {"index": 28},
            ],
            "contribs": [
                {
                    "index": 0,
                    "raw_name": "Abdelmoneim E M Kheir",
                    "role": "author",
                    "extra": {"seq": "first"},
                }
            ],
            "language": "en",
            "publisher": "Springer Nature",
            "pages": "34",
            "volume": "38",
            "ext_ids": {
                "doi": "10.1186/1824-7288-38-34",
                "wikidata_qid": "Q21198745",
                "pmid": "22823993",
                "pmcid": "PMC3411470",
                "core": "124865312",
            },
            "release_year": 2012,
            "release_stage": "published",
            "release_type": "article-journal",
            "container_id": "z4gdwga7tncvdfn2z2eb7civka",
            "work_id": "s3peps3ctfezjbq4gtbq4ibohm",
            "title": "Infantile colic, facts and fiction",
            "state": "active",
            "ident": "eacv2anmnfbi3dgco4lfxw2utm",
            "revision": "c1c8f483-b65f-43e8-9fe5-f796e89e8c50",
            "extra": {
                "crossref": {
                    "alternative-id": ["1824-7288-38-34"],
                    "type": "journal-article",
                }
            },
        }
