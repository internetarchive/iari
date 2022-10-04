from src.wcd_base_model import WcdBaseModel
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.helpers.console import console


class Message(WcdBaseModel):
    """This models a message sent thorugh RabbitMQ"""

    title: str = ""
    # This is a Wikidata QID representing an article to work on
    qid: str = ""

    def process_data(self):
        if self.title or self.qid:
            from src import WcdImportBot

            bot = WcdImportBot(wikibase=IASandboxWikibase())
            # TODO implement aborting if this article has recently been processed
            if self.title:
                bot.page_title = self.title
                bot.get_and_extract_page_by_title()
            if self.qid:
                bot.wdqid = self.qid
                bot.get_and_extract_page_by_wdqid()
        else:
            console.print("Did not get a title or a qid")
