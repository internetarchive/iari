# import hashlib
# import logging
# from typing import Any, Optional
#
# import config
# from src.models.exceptions import MissingInformationError
# from src.models.wikimedia.enums import WikimediaSite
# from src.wcd_base_model import WcdBaseModel
#
# logger = logging.getLogger(__name__)
#
#
# class Hashing(WcdBaseModel):
#     """Here we handle all the necessary hashing"""
#
#     # wikibase: Wikibase = IASandboxWikibase()
#     language_code: str = "en"
#     wikimedia_site: WikimediaSite = WikimediaSite.wikipedia
#     title: str = ""
#     article_wikidata_qid: str = ""
#     raw_template: str = ""
#     testing: bool = False
#     article: Optional[Any] = None
#     reference: Optional[Any] = None
#
#     def __generate_entity_updated_hash_key__(
#         self,
#     ) -> str:
#         """Key we use to lookup the timestamp in SSDB
#
#         We encode the information we need to make it
#         unique and quick to lookup of the timestamp"""
#         if not self.title and not self.article_wikidata_qid:
#             if not self.testing:
#                 raise MissingInformationError(
#                     "self.title and self.article_wikidata_qid was empty"
#                 )
#             else:
#                 # generate a nonsense hash to avoid test failure
#                 return hashlib.md5(f"testing-" f"updated".encode()).hexdigest()
#         if self.title:
#             title_or_wdqid = self.title
#         else:
#             title_or_wdqid = self.article_wikidata_qid
#         return hashlib.md5(
#             # f"{self.wikibase.title}-"
#             f"{title_or_wdqid}-"
#             f"{self.language_code}-"
#             f"{self.wikimedia_site.value}-"
#             f"updated".encode()
#         ).hexdigest()
#
#     # def generate_raw_reference_hash(self) -> str:
#     #     """Calculate the md5 hash used in the title of the wikipage"""
#     #     if not self.raw_template:
#     #         raise MissingInformationError("self.raw_template was empty")
#     #     # We lower case the whole thing first because we don't care about casing
#     #     return hashlib.md5(f"{self.raw_template.lower()}".encode()).hexdigest()
#
#     # def generate_article_hash(self) -> str:
#     #     """We generate a md5 hash of the article
#     #     We choose md5 because it is fast https://www.geeksforgeeks.org/difference-between-md5-and-sha1/"""
#     #     if not self.article:
#     #         MissingInformationError("self.article was None")
#     #     if self.article:
#     #         if not self.article.page_id:
#     #             if self.testing:
#     #                 self.article.page_id = 0
#     #             else:
#     #                 raise MissingInformationError("self.page_id was None")
#     #         logger.debug(
#     #             f"Generating hash based on: "
#     #             # f"{self.wikibase.title}"
#     #             f"{self.language_code}{self.article.page_id}"
#     #         )
#     #         return hashlib.md5(
#     #             # f"{self.wikibase.title}"
#     #             f"{self.language_code}{self.article.page_id}".encode()
#     #         ).hexdigest()
#     #     else:
#     #         return ""
#     #
#     # def generate_reference_hash(self) -> str:
#     #     """We generate a md5 hash of the page_reference as a unique
#     #     identifier for any given page_reference in a Wikipedia page
#     #     We choose md5 because it is fast https://www.geeksforgeeks.org/difference-between-md5-and-sha1/"""
#     #     if not self.reference:
#     #         MissingInformationError("self.reference was None")
#     #     if self.reference:
#     #         str2hash = ""
#     #         #  decide if we really trust doi to be unique.
#     #         #  See https://www.wikidata.org/wiki/Property_talk:P356
#     #         if self.reference.wikidata_qid:
#     #             # This is the external id we trust the most.
#     #             str2hash = self.reference.wikidata_qid
#     #         elif self.reference.doi:
#     #             # In WD there are as of 2022-07-11 25k violations here.
#     #             # Most are due to bad data at PubMed
#     #             # see https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P356#Unique_value
#     #             # and https://twitter.com/DennisPriskorn/status/1546475347851591680
#     #             str2hash = self.reference.doi
#     #         elif self.reference.pmid:
#     #             str2hash = self.reference.pmid
#     #         elif self.reference.isbn:
#     #             # We strip the dashes before hashing
#     #             str2hash = self.reference.isbn.replace("-", "")
#     #         #  decide if we really trust oclc to be unique
#     #         # See https://www.wikidata.org/wiki/Property_talk:P243
#     #         elif self.reference.oclc:
#     #             str2hash = self.reference.oclc
#     #         elif self.reference.url:
#     #             if config.include_url_in_hash_algorithm:
#     #                 str2hash = self.reference.url
#     #         # elif self.first_parameter:
#     #         #     if config.include_url_in_hash_algorithm:
#     #         #         str2hash = self.first_parameter
#     #
#     #         # DISABLED templates specific hashing for now because it is error
#     #         # prone and does not make it easy to avoid duplicates
#     #         # For example a news article might be cited with the publication date in one place but not in another.
#     #         # If we include the publication date in the hash we will end up with a duplicate in Wikibase.
#     #         # if self.template_name == "cite av media":
#     #         #     """{{cite AV media |people= |date= |title= |trans-title= |type=
#     #         #     |language= |url= |access-date= |archive-url= |archive-date=
#     #         #     |format= |time= |location= |publisher= |id= |isbn= |oclc= |quote= |ref=}}"""
#     #         #     # https://en.wikipedia.org/wiki/Template:Cite_AV_media
#     #         #     if self.doi is None:
#     #         #         if self.isbn is None:
#     #         #             str2hash = self.__hash_based_on_title_and_date__()
#     #         #         else:
#     #         #             str2hash = self.isbn
#     #         #     else:
#     #         #         str2hash = self.doi
#     #         # elif self.template_name == "cite book":
#     #         #     if self.isbn is None:
#     #         #         str2hash = self.__hash_based_on_title_and_publisher_and_date__()
#     #         #     else:
#     #         #         str2hash = self.isbn
#     #         # elif self.template_name == "cite journal":
#     #         #     if self.doi is None:
#     #         #         # Fallback first to PMID
#     #         #         if self.pmid is None:
#     #         #             str2hash = self.__hash_based_on_title_and_date__()
#     #         #         else:
#     #         #             str2hash = self.pmid
#     #         #     else:
#     #         #         str2hash = self.doi
#     #         # elif self.template_name == "cite magazine":
#     #         #     """{{cite magazine |last= |first= |date= |title= |url=
#     #         #     |magazine= |location= |publisher= |access-date=}}"""
#     #         #     if self.doi is None:
#     #         #         #  clean URL first?
#     #         #         if (self.title) is not None:
#     #         #             str2hash = self.title + self.isodate
#     #         #         else:
#     #         #             raise ValueError(
#     #         #                 f"did not get what we need to generate a hash, {self.dict()}"
#     #         #             )
#     #         #     else:
#     #         #         str2hash = self.doi
#     #         # elif self.template_name == "cite news":
#     #         #     if self.doi is None:
#     #         #         #  clean URL first?
#     #         #         if (self.title) is not None:
#     #         #             str2hash = self.title + self.isodate
#     #         #         else:
#     #         #             raise ValueError(
#     #         #                 f"did not get what we need to generate a hash, {self.dict()}"
#     #         #             )
#     #         #     else:
#     #         #         str2hash = self.doi
#     #         # elif self.template_name == "cite web":
#     #         #     if self.doi is None:
#     #         #         # Many of these references lead to pages without any publication
#     #         #         # dates unfortunately. e.g. https://www.billboard.com/artist/chk-chk-chk-2/chart-history/tlp/
#     #         #         #  clean URL first?
#     #         #         if self.url is not None:
#     #         #             str2hash = self.url
#     #         #         else:
#     #         #             raise ValueError(
#     #         #                 f"did not get what we need to generate a hash, {self.dict()}"
#     #         #             )
#     #         #     else:
#     #         #         str2hash = self.doi
#     #         # elif self.template_name == "url":
#     #         #     """Example:{{url|chkchkchk.net}}"""
#     #         #     if self.doi is None:
#     #         #         #  clean URL first?
#     #         #         if self.first_parameter is not None:
#     #         #             str2hash = self.first_parameter
#     #         #         else:
#     #         #             raise ValueError(
#     #         #                 f"did not get what we need to generate a hash, {self.dict()}"
#     #         #             )
#     #         #     else:
#     #         #         str2hash = self.doi
#     #         # else:
#     #         #     # Do we want a generic fallback?
#     #         #     pass
#     #         if str2hash:
#     #             return hashlib.md5(
#     #                 # f'{self.wikibase.title}'
#     #                 f'{str2hash.replace(" ", "").lower()}'.encode()
#     #             ).hexdigest()
#     #         else:
#     #             logger.warning(
#     #                 f"hashing not possible for this reference "
#     #                 f"because no identifier or url or first parameter was found "
#     #                 f"or they were turned of in config.py."
#     #             )
#     #             return ""
#     #     else:
#     #         return ""
