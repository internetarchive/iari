import asyncio
import json
import logging
from asyncio import AbstractEventLoop
from typing import Optional, Set

from aiohttp import ClientPayloadError  # type: ignore
from aiosseclient import aiosseclient  # type: ignore

import config
from src.models.wikimedia.enums import WikimediaSite
from src.models.wikimedia.recent_changes_api.event import WikimediaEvent
from src.wcd_base_model import WcdBaseModel


class EventStream(WcdBaseModel):
    """This models an event stream from WMF"""

    language_code: str = "en"
    event_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    event_count: int = 0
    earlier_events: Set[str] = set()
    max_events_during_testing: int = 0
    testing_publish_count = 0
    test_publishing = False
    loop: Optional[AbstractEventLoop]

    class Config:
        arbitrary_types_allowed = True

    async def __get_events__(self):
        """Get events from the event stream until missing identifier limit"""
        logger = logging.getLogger(__name__)
        self.event_count = 0
        # We run in a while loop so we can continue even if we get a ClientPayloadError
        run = True
        while run:
            try:
                async for event in aiosseclient(
                    "https://stream.wikimedia.org/v2/stream/recentchange",
                ):
                    # print(type(event))
                    data = json.loads(event.data)
                    # console.print(data)
                    wmf_event = WikimediaEvent(**data)
                    wmf_event.event_site = self.event_site
                    if (
                        wmf_event.title
                        and wmf_event.is_enwiki
                        and wmf_event.is_main_namespace
                        and not wmf_event.bot
                    ):
                        self.event_count += 1
                        # We import if in allow list or the first article we get which has a title
                        if wmf_event.title in config.title_allow_list or (
                            self.testing_publish_count == 0
                            and self.test_publishing is True
                        ):
                            # logger.info(f"Article in namespace main: {wmf_event.title}")
                            wmf_event.publish_to_article_queue()
                            self.testing_publish_count += 1
                        else:
                            if wmf_event.title not in config.title_allow_list:
                                logger.info(
                                    f"{wmf_event.title} not in allow list, skipping"
                                )
                    else:
                        logger.debug("skipped event")
                    if self.__reached_max_events__:
                        print("max events reached. breaking out of loop")
                        return

            except ClientPayloadError:
                logger.error("ClientPayloadError")
                continue
            if self.__reached_max_events__:
                print("Max events reached. Quitting")
                self.loop.close()

    def start_consuming(
        self,
    ):
        if self.language_code is None or self.event_site is None:
            raise ValueError("did not get what we need")
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.__get_events__())

    @property
    def __reached_max_events__(self) -> bool:
        """Check whether max events is more than 0 and if we reached it"""
        return bool(0 < self.max_events_during_testing <= self.event_count)
