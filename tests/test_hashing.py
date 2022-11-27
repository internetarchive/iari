from src.models.hashing import Hashing


class TestHashing:
    def test___entity_updated_hash__(self):
        h = Hashing()
        h.article_wikidata_qid = "Q1"
        # print(m.__entity_updated_hash__())
        assert "6571bcc708dbebba0616aaabd3d0e98a" == h.__generate_entity_updated_hash_key__()
        h.article_wikidata_qid = ""
        h.title = "Q1"
        # print(m.__entity_updated_hash__())
        assert "6571bcc708dbebba0616aaabd3d0e98a" == h.__generate_entity_updated_hash_key__()
