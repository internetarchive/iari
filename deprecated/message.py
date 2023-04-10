# from datetime import datetime
# from typing import Optional
#
# from src.helpers.console import console
# from src.models.wikibase import Wikibase
#
# from src.models.wikimedia.enums import WikimediaSite
# from src.wcd_base_model import WcdBaseModel
#
#
# class Message(WcdBaseModel):
#     """This models a message sent through RabbitMQ"""
#
#     title: str = ""
#     # This is a Wikidata QID representing an article to work on
#     article_wikidata_qid: str = ""
#     wikibase: Wikibase = IASandboxWikibase()
#     language_code: str = "en"
#     wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA
#     time_of_last_update: Optional[datetime]
#
#     def process_data(self, testing: bool = False):
#         if testing and not self.cache:
#             self.__setup_cache__()
#         if not self.cache:
#             raise ValueError("self.cache was None")
#         if self.title or self.article_wikidata_qid:
#             from src import WcdImportBot
#
#             bot = WcdImportBot(wikibase=IASandboxWikibase())
#             update_delay = UpdateDelay(object_=self, cache=self.cache)
#             if update_delay.time_to_update():
#                 if self.title:
#                     bot.page_title = self.title
#                     bot.get_and_extract_page_by_title()
#                 if self.article_wikidata_qid:
#                     raise DeprecationWarning(
#                         "deprecated because of failed test since 2.1.0-alpha2"
#                     )
#                     # bot.wikidata_qid = self.article_wikidata_qid
#                     # bot.get_and_extract_page_by_wdqid()
#         else:
#             console.print("Did not get a title or a article_wikidata_qid")
