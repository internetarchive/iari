from src.models.hash_ import Hash_


class TestHash_:
    def test___entity_updated_hash__(self):
        h = Hash_()
        h.article_wikidata_qid = "Q1"
        # print(m.__entity_updated_hash__())
        assert "6571bcc708dbebba0616aaabd3d0e98a" == h.__entity_updated_hash__()
        h.article_wikidata_qid = ""
        h.title = "Q1"
        # print(m.__entity_updated_hash__())
        assert "6571bcc708dbebba0616aaabd3d0e98a" == h.__entity_updated_hash__()
