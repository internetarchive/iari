from src.models.wikimedia.recent_changes_api.event_stream import EventStream


class TestEventStream:
    def test_start_consuming(self):
        es = EventStream(max_events_during_testing=1)
        es.start_consuming()
