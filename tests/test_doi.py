from unittest import TestCase


class TestDoi(TestCase):
    retracted_in_oa_but_not_wd = "10.1038/nature04695"
    retracted_in_wd_but_not_oa = "10.1126/SCIENCE.1074501"
    retracted_in_both = "10.1186/1824-7288-38-34"
    unretracted_in_either = "10.1136/GUT.52.12.1678"
    unretracted_in_either_lowercase = "10.1136/gut.52.12.1678"

    def test___lookup_doi_in_openalex_not_retracted(self):
        doi = Doi(doi=self.retracted_in_wd_but_not_oa)
        doi.__lookup_doi_in_openalex__()
        assert doi.found_in_openalex is True
        assert doi.marked_as_retracted_in_openalex is False
        assert doi.openalex_work_uri == "https://openalex.org/W2044307156"

    def test___lookup_doi_in_openalex_retracted(self):
        doi = Doi(doi=self.retracted_in_oa_but_not_wd)
        doi.__lookup_doi_in_openalex__()
        assert doi.found_in_openalex is True
        assert doi.marked_as_retracted_in_openalex is True
        assert doi.openalex_work_uri == "https://openalex.org/W2033363278"

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
        assert doi.get_cleaned_doi_object() == {
            "doi": "10.1186/1824-7288-38-34",
            "doi_lookup_done": True,
            "found_in_openalex": True,
            "found_in_wikidata": True,
            "marked_as_retracted_in_openalex": True,
            "marked_as_retracted_in_wikidata": True,
            "openalex_work_uri": "https://openalex.org/W2151284642",
            "wikidata_entity_qid": "Q21198745",
        }
