from unittest import TestCase

import config
from src.models.wikibase.enums import SupportedWikibase
from src.models.wikimedia.recent_changes_api import RecentChangesApi


class TestEventStream(TestCase):
    def test_start_consuming(self):
        """This starts up the ingestor, publishes the
        first enwiki article with a title and quits after 10 events"""
        es = RecentChangesApi(
            test_publishing=True,
            max_events_during_testing=config.max_events_during_testing,
            target_wikibase=SupportedWikibase.IASandboxWikibase,
        )
        es.start_consuming()
        assert es.testing_publish_count == 1
