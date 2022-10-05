import asyncio
import json
import logging
from typing import Set

from aiohttp import ClientPayloadError  # type: ignore
from aiosseclient import aiosseclient  # type: ignore

import config
from src.models.wikimedia.enterprise_api.event import WikimediaEvent
from src.models.wikimedia.enums import WikimediaSite
from src.wcd_base_model import WcdBaseModel


class EventStream(WcdBaseModel):
    """This models an event stream from WMF"""

    language_code: str = "en"
    event_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    event_count: int = 0
    earlier_events: Set[str] = set()
    max_events: int = config.max_events

    async def __get_events__(self):
        """Get events from the event stream until missing identifier limit"""
        logger = logging.getLogger(__name__)
        self.event_count = 0
        # We run in a while loop so we can continue even if we get a ClientPayloadError
        while True:
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
                        if wmf_event.title in config.title_allow_list:
                            # logger.info(f"Article in namespace main: {wmf_event.title}")
                            wmf_event.publish_to_article_queue()
                        else:
                            if wmf_event.title not in config.title_allow_list:
                                logger.info(
                                    f"{wmf_event.title} not in allow list, skipping"
                                )
                    else:
                        logger.debug("skipped event")
                    self.__quit_if_reached_max_events__()
            except ClientPayloadError:
                logger.error("ClientPayloadError")
                continue
            self.__quit_if_reached_max_events__()

    def start_consuming(
        self,
    ):
        if self.language_code is None or self.event_site is None:
            raise ValueError("did not get what we need")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__get_events__())

    def __quit_if_reached_max_events__(self):
        if 0 < self.max_events <= self.event_count:
            print("Max events reached. Quitting")
            exit(0)
