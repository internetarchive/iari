import logging
from datetime import datetime
from typing import Optional
from urllib.parse import quote

from src.models.exceptions import MissingInformationError
from src.models.message import Message
from src.models.wikibase import Wikibase
from src.models.wikimedia.enums import WikimediaEditType, WikimediaSite
from src.models.work_queue import WorkQueue
from src.wcd_base_model import WcdBaseModel

logger = logging.getLogger(__name__)


class Meta(WcdBaseModel):
    id: str
    dt: datetime
    domain: str
    offset: int


class WikimediaEvent(WcdBaseModel):
    """This models a WMF page update event from the Enterprise API
    It follows /mediawiki/recentchange/1.0.0"""

    meta: Meta
    bot: bool
    type: WikimediaEditType
    namespace: int
    title: str = ""
    event_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    wikibase: Optional[Wikibase]

    @property
    def domain(self):
        return self.meta.domain

    @property
    def is_enwiki(self):
        return bool(self.domain == "en.wikipedia.org")

    @property
    def is_main_namespace(self):
        return bool(self.namespace == 0)

    @property
    def language_code(self):
        return self.domain.replace(f".{self.event_site.value}.org", "")

    def url(self):
        return f"http://{self.domain}/wiki/{quote(self.title)}"

    def publish_to_article_queue(self):
        logger.debug("publish_to_article_queue: Running")
        if not self.wikibase:
            raise MissingInformationError("self.wikibase was None")
        logger.info(f"Publishing message with {self.title}")
        # TODO we should only create and connect to the work queue once so move this up to EventStream
        work_queue = WorkQueue(wikibase=self.wikibase)
        message = Message(title=self.title, wikibase=self.wikibase)
        work_queue.publish(message=message)
