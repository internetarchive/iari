from unittest import TestCase

import config
from src.models.wikimedia.recent_changes_api.event_stream import EventStream


class TestEventStream(TestCase):
    def test_start_consuming(self):
        """This starts up the ingestor, publishes the
        first enwiki article with a title and quits after 10 events"""
        es = EventStream(test_publishing=True, max_events=config.max_events_during_testing)
        es.start_consuming()
        assert es.testing_publish_count == 1