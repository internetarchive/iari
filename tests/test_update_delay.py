from datetime import datetime, timedelta

import config
from src.models.message import Message
from src.models.update_delay import UpdateDelay


class TestUpdateDelay:
    def test_time_to_update(self):
        """We expect this to be true because ??
        We pass testing to setup the cache"""
        ud = UpdateDelay(object_=Message(title="Test"))
        # First we ensure that a very early timestamp is present
        ud.__setup_cache__()
        ud.cache.set_title_or_wdqid_last_updated(
            key=ud.__get_entity_updated_hash_key__(), timestamp=123.123
        )
        # Then we test if it is time to update
        result = ud.time_to_update(testing=True)
        assert result is True

    def test___delay_time_has_passed__(self):
        ud = UpdateDelay(object_=Message())
        assert config.article_update_delay_in_hours < 48
        ud.time_of_last_update = datetime.now() - timedelta(days=2)
        assert ud.__delay_time_has_passed__() is True

    def test__get_timestamp_from_cache__message(self):
        ud = UpdateDelay(object_=Message(title="Test"))
        # First we ensure that the timestamp is present in the cache
        ud.__setup_cache__()
        ud.cache.set_title_or_wdqid_last_updated(
            key=ud.__get_entity_updated_hash_key__(), timestamp=123.123
        )
        # Then we check that we can correctly get it
        assert ud.__get_timestamp_from_cache__(testing=True) == 123.123

    def test__get_timestamp_from_cache__message_no_timestamp(self):
        ud = UpdateDelay(object_=Message(title="Theft"))
        # First we ensure that the timestamp is not present in the cache
        ud.__setup_cache__()
        ud.cache.delete_key(key=ud.__get_entity_updated_hash_key__())
        # Then we check that we get the empty result
        assert ud.__get_timestamp_from_cache__(testing=True) == 0.0

    def test_configuration_variables(self):
        """We test if we have sane settings"""
        assert config.article_update_delay_in_hours >= 1
        assert config.reference_update_delay_in_hours >= 24
