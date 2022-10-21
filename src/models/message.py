from datetime import datetime
from typing import Optional

from src import WcdWikibaseModel
from src.helpers.console import console
from src.models.update_delay import UpdateDelay
from src.models.wikibase import Wikibase
from src.models.wikibase.enums import SupportedWikibase
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.enums import WikimediaSite
from src.wcd_base_model import WcdBaseModel


class Message(WcdWikibaseModel):
    """This models a message sent through RabbitMQ.

    We default to IASandboxWikibase for now"""

    title: str = ""
    # This is a Wikidata QID representing an article to work on
    article_wikidata_qid: str = ""
    target_wikibase: SupportedWikibase = SupportedWikibase.IASandboxWikibase
    wikibase = IASandboxWikibase()
    language_code: str = "en"
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    time_of_last_update: Optional[datetime]

    def process_data(self):
        if self.title or self.article_wikidata_qid:
            from src import WcdImportBot

            bot = WcdImportBot(target_wikibase=self.target_wikibase, wikibase=self.wikibase)
            update_delay = UpdateDelay(object_=self)
            if update_delay.time_to_update:
                if self.title:
                    bot.page_title = self.title
                    bot.get_and_extract_page_by_title()
                if self.article_wikidata_qid:
                    bot.wikidata_qid = self.article_wikidata_qid
                    bot.get_and_extract_page_by_wdqid()
        else:
            console.print("Did not get a title or a article_wikidata_qid")
