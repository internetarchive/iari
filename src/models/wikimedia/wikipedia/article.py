import logging
from datetime import datetime
from typing import Optional

import requests
from dateutil.parser import isoparse
from pydantic import validate_arguments

import config
from src.models.api.job.article_job import ArticleJob
from src.models.basemodels.job import JobBaseModel
from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.wikimedia.enums import WikimediaDomain
from src.models.wikimedia.wikipedia.reference.extractor import (
    WikipediaReferenceExtractor,
)

logger = logging.getLogger(__name__)


class WikipediaArticle(JobBaseModel):
    """Models a WMF Wikipedia article

    Implementation details:
    Cache setup occurs only in this class and
    not in the classes below (ie Website and WikipediaReference)
    because of
    https://github.com/internetarchive/wcdimportbot/issues/261"""

    latest_revision_date: Optional[datetime]
    latest_revision_id: Optional[int]
    md5hash: Optional[str]
    page_id: int = 0
    wikimedia_domain: WikimediaDomain = WikimediaDomain.wikipedia
    wikitext: Optional[str]
    wdqid: str = ""
    found_in_wikipedia: bool = True
    extractor: Optional[WikipediaReferenceExtractor] = None
    check_urls: bool = False
    testing: bool = False
    job: ArticleJob
    # TODO add language_code to avoid enwiki hardcoding

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable
        extra = "forbid"  # dead: disable

    # @property
    # def absolute_url(self):
    #     return f"https://{self.language_code}.{self.wikimedia_site.value}.org/w/index.php?curid={self.page_id}"

    @property
    def is_redirect(self) -> bool:
        if "#REDIRECT" in str(self.wikitext)[:10]:
            return True
        else:
            return False

    @property
    def underscored_title(self):
        """Helper property"""
        if not self.job.title:
            raise ValueError("self.title was empty")
        return self.job.title.replace(" ", "_")

    @property
    def url(self):
        return self.job.url

    # @property
    # def wikibase_url(self):
    #     if self.wikibase.item_prefixed_wikibase:
    #         return f"{self.wikibase.wikibase_url}wiki/Item:{self.return_.item_qid}"
    #     else:
    #         return f"{self.wikibase.wikibase_url}wiki/{self.return_.item_qid}"

    # def __generate_hash__(self):
    #     hashing = Hashing(article=self, testing=True)
    #     self.md5hash = hashing.generate_article_hash()

    def fetch_and_extract_and_parse(self):
        from src.models.api import app

        app.logger.debug("fetch_and_extract_and_parse_and_generate_hash: running")
        app.logger.info("Extracting templates and parsing the references now")
        # We only fetch data from Wikipedia if we don't already have wikitext to work on
        if not self.wikitext:
            self.__fetch_page_data__()
        if self.is_redirect:
            logger.debug(
                "Skipped extraction and parsing because the article is a redirect"
            )
        elif not self.found_in_wikipedia:
            logger.debug(
                "Skipped extraction and parsing because the article was not found"
            )
        elif not self.is_redirect and self.found_in_wikipedia:
            if not self.wikitext:
                raise MissingInformationError("self.wikitext was empty")
            # We got what we need now to make the extraction and parsing
            # print(self.wikitext)
            self.extractor = WikipediaReferenceExtractor(
                wikitext=self.wikitext,
                # wikibase=self.wikibase,
                job=self.job,
            )
            self.extractor.extract_all_references()
            # self.__generate_hash__()
        else:
            raise Exception("This branch should never be hit.")

    def __fetch_page_data__(self) -> None:
        """This fetches metadata and the latest revision id
        and date from the MediaWiki REST v1 API if needed"""
        from src.models.api import app

        app.logger.debug("__fetch_page_data__: Running")
        self.__check_if_title_is_empty__()
        if (
            not self.latest_revision_id
            or not self.latest_revision_date
            or not self.wikitext
            or not self.page_id
        ):
            # This is needed to support e.g. https://en.wikipedia.org/wiki/Musk%C3%B6_naval_base or
            # https://en.wikipedia.org/wiki/GNU/Linux_naming_controversy
            url = (
                f"https://{self.job.lang.value}.{self.job.domain.value}/"
                f"w/rest.php/v1/page/{self.job.quoted_title}"
            )
            headers = {"User-Agent": config.user_agent}
            response = requests.get(url, headers=headers)
            # console.print(response.json())
            if response.status_code == 200:
                data = response.json()
                # TODO read up on the documentation to find out if this is reliable
                self.latest_revision_id = int(data["latest"]["id"])
                self.latest_revision_date = isoparse(data["latest"]["timestamp"])
                self.page_id = int(data["id"])
                logger.debug(f"Got pageid: {self.page_id}")
                self.wikitext = data["source"]
            elif response.status_code == 404:
                self.found_in_wikipedia = False
                logger.error(
                    f"Could not fetch page data from {self.wikimedia_domain.name} because of 404. See {url}"
                )
            else:
                raise WikipediaApiFetchError(
                    f"Could not fetch page data. Got {response.status_code} from {url}"
                )
        else:
            logger.info(
                "Not fetching data via the Wikipedia REST API. We have already got all the data we need"
            )

    # def __fetch_wikidata_qid__(self):
    #     """Fetch the Wikidata QID so we can efficiently look up pages via JS"""
    #     url = (
    #         f"https://{self.language_code}.wikipedia.org/w/api.php?action=query&prop="
    #         f"pageprops&ppprop=wikibase_item&redirects=1&titles={quote(self.title)}&format=json"
    #     )
    #     headers = {"User-Agent": config.user_agent}
    #     logger.debug(url)
    #     response = requests.get(url, headers=headers)
    #     if response.status_code == 200:
    #         # console.print(response.text)
    #         data = response.json()
    #         # console.print(data)
    #         query = data.get("query")
    #         if query:
    #             pages = query.get("pages")
    #             if pages:
    #                 if len(pages):
    #                     for page in pages:
    #                         page_data = pages[page]
    #                         print(page_data)
    #                         if "pageprops" in page_data.keys():
    #                             if page_data["pageprops"]:
    #                                 if page_data["pageprops"]["wikibase_item"]:
    #                                     self.wikidata_qid = page_data["pageprops"][
    #                                         "wikibase_item"
    #                                     ]
    #                                 else:
    #                                     raise MissingInformationError(
    #                                         f"Did not get any wikibase_item from MediaWiki, see {url}"
    #                                     )
    #                             else:
    #                                 raise MissingInformationError(
    #                                     f"Did not get any pageprops from MediaWiki, see {url}"
    #                                 )
    #                         else:
    #                             MissingInformationError("no pageprops")
    #                         # We only care about the first page
    #                         break
    #                 else:
    #                     raise MissingInformationError(
    #                         f"Did not get any pages from MediaWiki, see {url}"
    #                     )
    #             else:
    #                 raise MissingInformationError(
    #                     f"Did not get any pages-key from MediaWiki, see {url}"
    #                 )
    #         else:
    #             raise MissingInformationError(
    #                 f"Did not get any query from MediaWiki, see {url}"
    #             )
    #         logger.info(f"Found Wikidata QID: {self.wikidata_qid}")

    def __parse_templates__(self):
        """Disabled method because of rewrite"""
        # if not self.cache:
        #     self.__setup_cache__()
        # if not self.cache:
        #     raise ValueError("could not setup the cache")
        # console.print(
        #     f"Parsing {self.number_of_reference_templates} reference "
        #     f"templates out of {self.number_of_templates} templates in "
        #     f"total from {self.title}, see {self.url}"
        # )
        # for template_name, content, raw_template in self.template_triples:
        #     # logger.debug(f"working on {template_name}")
        #     if template_name.lower() in config.supported_templates:
        #         parsed_template = self.__fix_keys__(json.loads(json.dumps(content)))
        #         parsed_template["template_name"] = template_name.lower()
        #         if config.loglevel == logging.DEBUG:
        #             logger.debug("parsed_template:")
        #             console.print(parsed_template)
        #             # press_enter_to_continue()
        #         schema = EnglishWikipediaReferenceSchema()
        #         try:
        #             reference: Optional[WikipediaReference] = schema.load(
        #                 parsed_template
        #             )
        #         except ValidationError as error:
        #             logger.debug(f"Validation error: {error}")
        #             schema_log_file = "schema_errors.log"
        #             self.__log_to_file__(message=str(error), file_name=schema_log_file)
        #             logger.error(
        #                 f"This reference was skipped because an unknown "
        #                 f"field was found. See the file '{schema_log_file}' for details"
        #             )
        #             reference = None
        #         # DISABLED partial loading because it does not work :/
        #         # if not reference:
        #         #     logger.info("Trying now to deserialize the reference partially")
        #         #     # Load partially (ie. ignore the unknown field)
        #         #     reference: WikipediaReference = schema.load(
        #         #         parsed_template, partial=True
        #         #     )
        #         # if not reference:
        #         #     raise ValueError("This reference could not be deserialized. :/")
        #         # else:
        #         if reference:
        #             reference.wikibase = self.wikibase
        #             # This is because of https://github.com/internetarchive/wcdimportbot/issues/261
        #             reference.cache = self.cache
        #             # We want the raw templates
        #             reference.raw_template = raw_template
        #             reference.finish_parsing_and_generate_hash()
        #             # Handle duplicates:
        #             if reference.md5hash in [
        #                 reference.md5hash
        #                 for reference in self.references
        #                 if reference.md5hash is not None
        #             ]:
        #                 logging.debug(
        #                     "Skipping reference already present "
        #                     "in the list to avoid duplicates"
        #                 )
        #             # if config.loglevel == logging.DEBUG:
        #             #     console.print(reference.dict())
        #             else:
        #                 self.references.append(reference)
        #     else:
        #         if config.debug_unsupported_templates:
        #             logger.debug(f"Template '{template_name.lower()}' not supported")

    # def __print_hash_statistics__(self):
    #     if self.extractor:
    #         logger.info(
    #             f"Hashed {self.extractor.percent_of_content_references_with_a_hash} percent of "
    #             f"{len(self.extractor.references)} references on page {self.title}"
    #         )

    # def __upload_page_and_references__(self):
    #     # TODO rename this method to "__upload_new_article_item__"
    #     console.print(f"Importing page '{self.title}'")
    #     self.__setup_wikibase_crud_create__()
    #     self.return_ = (
    #         self.wikibase_crud_create.prepare_and_upload_wikipedia_article_item(
    #             wikipedia_article=self,
    #         )
    #     )
    #     if self.return_ is None:
    #         raise ValueError("wcdqid was None")
    #     self.cache.add_page(wikipedia_article=self, wcdqid=self.return_.item_qid)
    #     if self.return_.uploaded_now:
    #         console.print(
    #             f"Finished uploading {self.title} to Wikibase, "
    #             f"see {self.url} and {self.wikibase_url}"
    #         )
    #     else:
    #         # TODO comment out the below code and fail with an exception instead
    #         # This branch is hit e.g. when the cache has not been synced with the wikibase
    #         console.print(
    #             f"{self.title} already exists in {self.wikibase.__repr_name__()}, "
    #             f"see {self.url} and {self.wikibase_url}. \nPlease run the bot with --rebuild-cache "
    #             f"to speed up the process."
    #         )
    #         self.__compare_data_and_update__()

    # TODO comment out before 3.0.0-alpha0
    # def __upload_references_and_websites_if_missing__(self, testing: bool = False):
    #     """Go through each reference and upload if missing to Wikibase"""
    #     logger.debug("__upload_references_and_websites_if_missing__: Running")
    #     # if testing and not self.cache:
    #     #     self.__setup_cache__()
    #     # if not self.cache:
    #     #     raise ValueError("self.cache could not be setup")
    #     updated_references = []
    #     count = 1
    #     total = len(self.references)
    #     for reference in self.references:
    #         console.print(
    #             f"Working on reference {count}/{total} from article {self.title}"
    #         )
    #         # Here we check for an existing website item
    #         if reference.has_first_level_domain_url_hash:
    #             with console.status(
    #                 f"Linking to or uploading new website item for reference "
    #                 f"with link to {reference.first_level_domain_of_url}"
    #             ):
    #                 # Here we get the reference with the first_level_domain_of_url WCDQID back
    #                 # We add the cache because of https://github.com/internetarchive/wcdimportbot/issues/261
    #                 reference.website_item = Website(
    #                     reference=reference, wikibase=self.wikibase, cache=self.cache
    #                 )
    #                 reference.website_item.check_and_upload_website_item_to_wikibase_if_missing(
    #                     wikipedia_article=self
    #                 )
    #         # Here we check for an existing reference item
    #         if reference.has_hash:
    #             # logger.debug(f"has_hash was True for md5hash: {reference.md5hash}")
    #             with console.status(f"Creating the reference item if missing"):
    #                 # Here we get the reference with WikibaseReturn back
    #                 reference.check_and_upload_reference_item_to_wikibase_if_missing()
    #                 if not reference.return_:
    #                     raise MissingInformationError(
    #                         "reference.return_ was None and is needed "
    #                         "to judge whether to compare or not"
    #                     )
    #                 # else:
    #                 #     console.print(reference.return_.dict())
    #                 # exit()
    #                 # We only store last update information for references with a hash/item
    #                 reference.insert_last_update_timestamp()
    #         updated_references.append(reference)
    #         count += 1
    #     self.references = updated_references
    #
    # # TODO comment out before 3.0.0-alpha0
    # def extract_and_parse_and_upload_missing_items_to_wikibase(self) -> None:
    #     """Extract the references and upload first
    #     the references and then the page to Wikibase
    #
    #     First we fetch the page data and generate the hash,
    #     then we setup the Wikibase and extract and parse
    #     the references.
    #
    #     Then we upload the references and websites if missing
    #     and then we either upload the page or if missing
    #     compare and upload any missing claims.
    #
    #     Lastly we store the timestamp in the cache"""
    #     logger.debug("extract_and_upload_to_wikibase: Running")
    #     if not self.cache:
    #         self.__setup_cache__()
    #     if not self.cache:
    #         raise ValueError("could not setup the cache :/")
    #     self.__fetch_page_data__()
    #     if not self.is_redirect and self.found_in_wikipedia:
    #         self.__fetch_wikidata_qid__()
    #         self.__generate_hash__()
    #         self.__setup_wikibase_crud_create__()
    #         self.__extract_and_parse_references__()
    #         if self.extractor and self.extractor.number_of_references <= 500:
    #             self.__upload_references_and_websites_if_missing__()
    #             if not self.__page_has_already_been_uploaded__():
    #                 self.__upload_page_and_references__()
    #             else:
    #                 self.__compare_data_and_update__()
    #             # We update the timestamp no matter what action we took above
    #             self.__insert_last_update_timestamp__()
    #     else:
    #         if self.is_redirect:
    #             console.print("This page is a redirect to another page. Not importing.")

    # TODO remove this old code
    # def __get_title_from_event__(self):
    #     self.title = self.wikimedia_event.page_title
    #     if self.title is None or self.title == "":
    #         raise ValueError("title not set correctly")
    # def __find_references_without_hashes__(self):
    #     references_without_hashes = [
    #         page_reference for page_reference in self.references if page_reference.md5hash is None
    #     ]
    #     logger.info(f"references_without_hashes: {len(references_without_hashes)}")
    #     if references_without_hashes is None:
    #         self.references_without_hashes = []
    #     else:
    #         self.references_without_hashes = references_without_hashes
    #     self.number_of_references_without_a_hash = len(self.references_without_hashes)
    #     logger.info(
    #         f"number_of_references_without_a_hash: {self.number_of_references_without_a_hash}"
    #     )
    # def __get_wikipedia_page_from_event__(self):
    #     """Get the page from Wikipedia"""
    #     logger.info("Fetching the wikitext")
    #     self.pywikibot_page = pywikibot.Page(
    #         self.wikimedia_event.event_stream.pywikibot_site, self.title
    #     )

    @validate_arguments
    def __get_wikipedia_article_from_wdqid__(self):
        raise DeprecationWarning("deprecated because of failed test since 2.1.0-alpha2")
        # self.__get_title_from_wikidata__()
        # self.__get_wikipedia_article_from_title__()

    def __get_title_from_wikidata__(self):
        raise DeprecationWarning("deprecated because of failed test since 2.1.0-alpha2")
        # logger.debug("__get_title_from_wikidata__: Running")
        # from wikibaseintegrator import wbi_helpers  # type: ignore
        #
        # # https://www.wikidata.org/w/api.php?action=wbgetentities
        # &ids=Q180736&props=sitelinks/urls&languages=az&languagefallback=&sitefilter=enwiki&formatversion=2
        # #  avoid hardcoding enwiki here
        # data = {
        #     "action": "wbgetentities",
        #     "props": "sitelinks/urls",
        #     "ids": self.wdqid,
        #     "sitefilter": "enwiki",
        # }
        # result = wbi_helpers.mediawiki_api_call_helper(
        #     data=data, allow_anonymous=True, user_agent=config.user_agent
        # )
        # """{
        #     "entities": {
        #         "Q180736": {
        #             "type": "item",
        #             "id": "Q180736",
        #             "sitelinks": {
        #                 "enwiki": {
        #                     "site": "enwiki",
        #                     "title": "Les Misérables",
        #                     "badges": [],
        #                     "url": "https://en.wikipedia.org/wiki/Les_Mis%C3%A9rables"
        #                 }
        #             }
        #         }
        #     },
        #     "success": 1
        # }"""
        # entities = result.get("entities")
        # if entities:
        #     for entity in entities:
        #         # console.print(entity)
        #         # we only care about the first
        #         sitelinks = entities[entity].get("sitelinks")
        #         # console.print(sitelinks)
        #         if sitelinks:
        #             enwiki = sitelinks.get("enwiki")
        #             if enwiki:
        #                 logger.debug(f"got title: {self.title}")
        #                 self.title = enwiki.get("title")
        #             else:
        #                 raise MissingInformationError(
        #                     "no enwiki sitelink from Wikidata"
        #                 )
        #         else:
        #             raise MissingInformationError(f"no sitelinks from Wikidata, got {entities}")
        # else:
        #     raise MissingInformationError("no entities from Wikidata")

    def __check_if_title_is_empty__(self):
        if not self.job.title:
            raise MissingInformationError("self.job.title was empty string")
