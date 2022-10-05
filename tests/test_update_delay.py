from datetime import datetime, timedelta

from src.models.message import Message
from src.models.update_delay import UpdateDelay


class TestUpdateDelay:
    def test_time_to_update(self):
        ud = UpdateDelay(object_=Message())
        ud.time_of_last_update = datetime.now() - timedelta(days=2)
        assert ud.time_to_update is True

    def test___delay_time_has_passed__(self):
        ud = UpdateDelay(object_=Message())
        ud.time_of_last_update = datetime.now() - timedelta(days=2)
        assert ud.__delay_time_has_passed__() is True

    # def test___delay_time_has_passed__(self):
    #     m = Message()
    #     m.time_of_last_update = datetime.now() - timedelta(days=2)
    #     assert m.__delay_time_has_passed__() is True
    #
