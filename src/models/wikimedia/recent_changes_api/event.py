import json
import logging
from datetime import datetime
from urllib.parse import quote

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
        logger.info(f"Publishing message with {self.title}")
        work_queue = WorkQueue()
        work_queue.publish(message=bytes(json.dumps(dict(title=self.title)), "utf-8"))
