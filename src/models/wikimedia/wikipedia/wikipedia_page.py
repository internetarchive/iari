from __future__ import annotations

import hashlib
import json
import logging
from typing import List, Any, Optional, Dict

import pywikibot  # type: ignore
from pydantic import BaseModel, validate_arguments
from pywikibot import Page, Site

import config
from src.models.wikicitations.enums import WCDItem
from src.models.cache import Cache
from src.models.wikimedia.enums import WikimediaSite
from src.models.wikimedia.wikipedia.templates.english_wikipedia_page_reference import (
    EnglishWikipediaPageReferenceSchema,
)
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

logger = logging.getLogger(__name__)


class WikipediaPage(BaseModel):
    """Models a WMF Wikipedia page"""

    cache: Optional[Cache]
    language_code: str = "en"
    language_wcditem: WCDItem = WCDItem.ENGLISH_WIKIPEDIA
    max_number_of_item_citations_to_upload: Optional[int]
    md5hash: Optional[str]
    percent_of_references_with_a_hash: Optional[int]
    pywikibot_page: Optional[Page]
    pywikibot_site: Optional[Any]
    references: Optional[List[WikipediaPageReference]]
    uploaded_item_citations: int = 0
    wikicitations: Optional[Any]  # WikiCitaitons
    wikicitations_qid: Optional[str]
    wikimedia_event: Optional[
        Any  # We can't type this with WikimediaEvent because of pydantic
    ]
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA

    class Config:
        arbitrary_types_allowed = True

    @property
    def absolute_url(self):
        return f"https://{self.language_code}.{self.wikimedia_site.value}.org/w/index.php?curid={self.page_id}"

    @property
    def number_of_hashed_references(self):
        return len(
            [
                reference
                for reference in self.references
                if reference.md5hash is not None
            ]
        )

    @property
    def number_of_references(self):
        return len(self.references)

    @property
    def page_id(self):
        """Helper property"""
        # this id is useful when talking to WikipediaCitations because it is unique
        return int(self.pywikibot_page.pageid)

    @property
    def percent_of_references_with_a_hash(self):
        if self.number_of_references == 0:
            return 0
        else:
            return int(
                self.number_of_hashed_references * 100 / self.number_of_references
            )

    @property
    def revision_id(self):
        revid = self.pywikibot_page.latest_revision_id
        if revid is not None:
            return revid
        else:
            raise ValueError("got no revision id form pywikibot")

    @property
    def title(self):
        """Helper property"""
        return self.pywikibot_page.title()

    @property
    def url(self):
        return (
            f"https://{self.language_code}.{self.wikimedia_site.value}.org/"
            f"wiki/{self.pywikibot_page.title(underscore=True)}"
        )

    @property
    def wikicitations_url(self):
        return f"{config.wikibase_url}/" f"wiki/Item:{self.wikicitations_qid}"

    def __calculate_hashed_template_distribution__(self):
        raise NotImplementedError("To be written")

    @validate_arguments
    def __check_and_upload_reference_item_to_wikicitations_if_missing__(
        self, reference: WikipediaPageReference
    ):
        logger.debug("Checking and uploading page references")
        if reference is None:
            raise ValueError("reference was None")
        if config.cache_and_upload_enabled is not None:
            wcdqid = self.__get_reference_wcdqid_from_cache__(reference=reference)
            if wcdqid is not None:
                logger.debug(f"Got wcdqid:{wcdqid} from the cache")
                reference.wikicitations_qid = wcdqid
            else:
                if self.max_number_of_item_citations_to_upload is not None:
                    if (
                        self.uploaded_item_citations
                        < self.max_number_of_item_citations_to_upload
                    ):
                        reference = self.__upload_reference_and_insert_in_the_cache__(
                            reference=reference
                        )
                        self.uploaded_item_citations += 1
                        logger.info(
                            f"Added {self.uploaded_item_citations} out "
                            f"of maximum {self.max_number_of_item_citations_to_upload}"
                        )
                    else:
                        logger.info(
                            f"Skipping upload of this reference because the maximum number of "
                            f"{self.max_number_of_item_citations_to_upload} has been reached"
                        )
                else:
                    reference = self.__upload_reference_and_insert_in_the_cache__(
                        reference=reference
                    )
        return reference

    @validate_arguments
    def __check_and_upload_website_item_to_wikicitations_if_missing__(
        self, reference: WikipediaPageReference
    ):
        logger.debug("Checking and uploading website item")
        if reference is None:
            raise ValueError("reference was None")
        if config.cache_and_upload_enabled is not None:
            wcdqid = self.__get_website_wcdqid_from_cache__(reference=reference)
            if wcdqid is not None:
                logger.debug(f"Got wcdqid:{wcdqid} from the cache")
                reference.first_level_domain_of_url_qid = wcdqid
            else:
                reference = self.__upload_website_and_insert_in_the_cache__(
                    reference=reference
                )
                logger.info(f"Added website item to WCD")
        return reference

    def __extract_and_parse_references__(self):
        logger.info("Extracting references now")
        # if self.wikimedia_event is not None:
        #     # raise ValueError("wikimedia_event was None")
        #     self.__get_title_from_event__()
        #     self.__get_wikipedia_page_from_event__()
        # elif self.title is not None:
        #     if self.pywikibot_site is None:
        #         raise ValueError("self.pywikibot_site was None")
        #     self.__get_wikipedia_page_from_title__()
        # else:
        if self.pywikibot_page is None:
            raise ValueError("self.pywikibot_page was None")
        self.__parse_templates__()
        self.__print_hash_statistics__()

    @staticmethod
    def __fix_class_key__(dictionary: Dict[str, Any]) -> Dict[str, Any]:
        """convert "class" key to "_class" to avoid collision with reserved python expression"""
        newdict = {}
        for key in dictionary:
            if key == "class":
                new_key = "news_class"
                newdict[new_key] = dictionary[key]
            else:
                newdict[key] = dictionary[key]
        return newdict

    @staticmethod
    def __fix_aliases__(dictionary: Dict[str, Any]) -> Dict[str, Any]:
        """Replace alias keys"""
        replacements = dict(
            accessdate="access_date",
            archiveurl="archive_url",
            archivedate="archive_date",
            ISBN="isbn",
            authorlink1="author_link1",
            authorlink2="author_link2",
            authorlink3="author_link3",
            authorlink4="author_link4",
            authorlink5="author_link5",
            authorlink="author_link",
        )
        newdict = {}
        for key in dictionary:
            replacement_made = False
            for replacement in replacements:
                if replacement == key:
                    new_key = replacements[key]
                    logger.debug(f"Replacing key {key} with {new_key}")
                    newdict[new_key] = dictionary[key]
                    replacement_made = True
            if not replacement_made:
                newdict[key] = dictionary[key]
        return newdict

    @staticmethod
    def __fix_dash__(dictionary: Dict[str, Any]) -> Dict[str, Any]:
        newdict = {}
        for key in dictionary:
            if "-" in key:
                new_key = key.replace("-", "_")
                newdict[new_key] = dictionary[key]
            else:
                newdict[key] = dictionary[key]
        return newdict

    def __fix_keys__(self, dictionary: Dict[str, Any]) -> Dict[str, Any]:
        dictionary = self.__fix_class_key__(dictionary=dictionary)
        dictionary = self.__fix_aliases__(dictionary=dictionary)
        return self.__fix_dash__(dictionary=dictionary)

    def __generate_hash__(self):
        """We generate a md5 hash of the page_reference as a unique identifier for any given page_reference in a Wikipedia page
        We choose md5 because it is fast https://www.geeksforgeeks.org/difference-between-md5-and-sha1/"""
        self.md5hash = hashlib.md5(
            f"{self.language_code}{self.page_id}".encode()
        ).hexdigest()
        logger.debug(self.md5hash)

    def __get_reference_wcdqid_from_cache__(
        self, reference: WikipediaPageReference
    ) -> Optional[str]:
        if self.cache is None:
            self.__setup_cache__()
        wcdqid = self.cache.check_reference_and_get_wikicitations_qid(
            reference=reference
        )
        logger.debug(f"result from the cache:{wcdqid}")
        return wcdqid

    def __get_website_wcdqid_from_cache__(
        self, reference: WikipediaPageReference
    ) -> Optional[str]:
        if self.cache is None:
            self.__setup_cache__()
        wcdqid = self.cache.check_website_and_get_wikicitations_qid(reference=reference)
        logger.debug(f"result from the cache:{wcdqid}")
        return wcdqid

    @validate_arguments
    def __get_wikipedia_page_from_title__(self, title: str):
        """Get the page from Wikipedia"""
        self.__prepare_pywiki_site__()
        logger.info("Fetching the wikitext")
        if self.pywikibot_site is None:
            raise ValueError("did not get what we need")
        self.pywikibot_page = pywikibot.Page(self.pywikibot_site, title)

        # this id is useful when talking to WikipediaCitations because it is unique
        # self.page_id = int(self.pywikibot_page.pageid)

    def __insert_reference_in_cache__(
        self, reference: WikipediaPageReference, wcdqid: str
    ):
        logger.debug("__insert_in_cache__: Running")
        self.cache.add_reference(reference=reference, wcdqid=wcdqid)
        logger.info("Reference inserted into the hash database")

    def __page_has_already_been_uploaded__(self) -> bool:
        """This checks whether the page has already been uploaded by checking the cache"""
        if self.cache is None:
            self.__setup_cache__()
        wcdqid = self.cache.check_page_and_get_wikicitations_qid(wikipedia_page=self)
        if wcdqid is None:
            logger.debug("Page not found in the cache")
            return False
        else:
            logger.debug("Page found in the cache")
            return True
    def __insert_website_in_cache__(
        self, reference: WikipediaPageReference, wcdqid: str
    ):
        logger.debug("__insert_website_in_cache__: Running")
        self.cache.add_website(reference=reference, wcdqid=wcdqid)
        logger.info("Reference inserted into the hash database")

    def __parse_templates__(self):
        """We parse all the templates into WikipediaPageReferences"""
        raw = self.pywikibot_page.raw_extracted_templates
        number_of_templates = len(raw)
        logger.info(
            f"Parsing {number_of_templates} templates from {self.pywikibot_page.title()}, see {self.url}"
        )
        self.references = []
        for template_name, content in raw:
            # logger.debug(f"working on {template_name}")
            if template_name.lower() in config.supported_templates:
                parsed_template = self.__fix_keys__(json.loads(json.dumps(content)))
                parsed_template["template_name"] = template_name.lower()
                logger.debug(parsed_template)
                schema = EnglishWikipediaPageReferenceSchema()
                reference: WikipediaPageReference = schema.load(parsed_template)
                reference.finish_parsing_and_generate_hash()
                # if config.loglevel == logging.DEBUG:
                #     console.print(reference.dict())
                self.references.append(reference)
            else:
                if config.debug_unsupported_templates:
                    logger.debug(f"Template '{template_name.lower()}' not supported")

    def __prepare_pywiki_site__(self):
        if (self.language_code and self.wikimedia_site) is not None:
            self.pywikibot_site = Site(
                code=self.language_code, fam=self.wikimedia_site.value
            )
        else:
            raise ValueError("did not get what we need")

    def __print_hash_statistics__(self):
        logger.info(
            f"Hashed {self.percent_of_references_with_a_hash} percent of "
            f"{len(self.references)} references on page {self.pywikibot_page.title()}"
        )

    def __setup_cache__(self):
        self.cache = Cache()
        self.cache.connect()

    def __setup_wikicitations__(self):
        from src.models.wikicitations import WikiCitations

        self.wikicitations = WikiCitations(
            language_code=self.language_code, language_wcditem=self.language_wcditem
        )

    @validate_arguments
    def __upload_reference_to_wikicitations__(
        self, reference: WikipediaPageReference
    ) -> str:
        logger.debug("__upload_reference_to_wikicitations__: Running")
        if self.wikicitations is None:
            self.__setup_wikicitations__()
        wcdqid = self.wikicitations.prepare_and_upload_reference_item(
            page_reference=reference, wikipedia_page=self
        )
        if wcdqid is None and config.cache_and_upload_enabled is True:
            raise ValueError(
                "Got None instead of WCDQID when trying to upload to WikiCitations"
            )
        return wcdqid

    @validate_arguments
    def __upload_reference_and_insert_in_the_cache__(
        self, reference: WikipediaPageReference
    ):
        # Here we get the reference back with WCDQID
        if config.cache_and_upload_enabled:
            wcdqid = self.__upload_reference_to_wikicitations__(reference=reference)
            if wcdqid is None:
                raise ValueError("WCDQID was None")
            if reference.md5hash is None:
                raise ValueError("hash was None")
            logger.debug(
                f"Hash before insertion: {reference.md5hash}. "
                f"WCDQID before insertion: {wcdqid}"
            )
            self.__insert_reference_in_cache__(reference=reference, wcdqid=wcdqid)
            reference.wikicitations_qid = wcdqid
        return reference

    @validate_arguments
    def __upload_website_and_insert_in_the_cache__(
        self, reference: WikipediaPageReference
    ):
        # Here we get the reference back with WCDQID
        if config.cache_and_upload_enabled:
            wcdqid = self.__upload_website_to_wikicitations__(reference=reference)
            if wcdqid is None:
                raise ValueError("WCDQID was None")
            if reference.first_level_domain_of_url_hash is None:
                raise ValueError("first_level_domain_of_url_hash was None")
            logger.debug(
                f"Hash before insertion: {reference.first_level_domain_of_url_hash}. "
                f"WCDQID before insertion: {wcdqid}"
            )
            self.__insert_reference_in_cache__(reference=reference, wcdqid=wcdqid)
            reference.wikicitations_qid = wcdqid
        return reference

    def __upload_references_and_websites_if_missing__(self):
        """Go through each reference and upload if missing to WikiCitations"""
        updated_references = []
        for reference in self.references:
            if reference.has_first_level_domain_url_hash:
                # Here we get the reference with the first_level_domain_of_url WCDQID back
                reference = (
                    self.__check_and_upload_website_item_to_wikicitations_if_missing__(
                        reference=reference
                    )
                )
            if reference.has_hash:
                # Here we get the reference with the WCDQID back
                reference = self.__check_and_upload_reference_item_to_wikicitations_if_missing__(
                    reference=reference
                )
            updated_references.append(reference)
        self.references = updated_references

    def export_to_dataframe(self):
        # TODO make it easy to quantify the references with pandas
        raise NotImplementedError("To be written")

    def extract_and_upload_to_wikicitations(self):
        """Extract the references and upload first
        the references and then the page to WikiCitations"""
        # First we check if this page has already been uploaded
        self.__generate_hash__()
        if not self.page_has_already_been_uploaded():
            logger.info(
                "This page is missing from WikiCitations according to the cache"
            )
            self.__setup_wikicitations__()
            # extract references and create items for the missing ones first
            self.__extract_and_parse_references__()
            self.__upload_references_and_websites_if_missing__()
            # upload a new item for the page with links to all the page_reference items
            wcdqid = self.wikicitations.prepare_and_upload_wikipedia_page_item(
                wikipedia_page=self,
            )
            if config.cache_and_upload_enabled is True:
                if wcdqid is None:
                    raise ValueError("wcdqid was None")
                self.cache.add_page(wikipedia_page=self, wcdqid=wcdqid)
        else:
            logger.info("This page has already been uploaded to WikiCitations")

    # def __match_subjects__(self):
    #     logger.info(f"Matching subjects from {len(self.dois) - self.number_of_missing_dois} DOIs")
    #     [doi.wikidata_scientific_item.crossref_engine.work.match_subjects_to_qids() for doi in self.dois
    #      if (
    #              doi.wikidata_scientific_item.doi_found_in_wikidata and
    #              doi.wikidata_scientific_item.crossref_engine is not None and
    #              doi.wikidata_scientific_item.crossref_engine.work is not None
    #      )]
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
