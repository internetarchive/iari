from src.models.wikimedia.enterprise_api.event_stream import EventStream


class TestEventStream:
    def test_start_consuming(self):
        es = EventStream(max_events=1)
        es.start_consuming()
