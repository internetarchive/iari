from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from typing import List, Any, Optional, Dict

import requests
from dateutil.parser import isoparse
from pydantic import BaseModel, validate_arguments, NoneStr

import config
from src.helpers.template_extraction import extract_templates_and_params
from src.models.cache import Cache
from src.models.wikicitations.enums import WCDItem
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
    latest_revision_date: Optional[datetime]
    latest_revision_id: Optional[int]
    max_number_of_item_citations_to_upload: Optional[int]
    md5hash: Optional[str]
    page_id: Optional[int]
    percent_of_references_with_a_hash: Optional[int]
    references: Optional[List[WikipediaPageReference]]
    title: NoneStr
    uploaded_item_citations: int = 0
    wikicitations: Optional[Any]  # WikiCitaitons
    wikicitations_qid: Optional[str]
    wikimedia_event: Optional[
        Any  # We can't type this with WikimediaEvent because of pydantic
    ]
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    wikitext: NoneStr

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
    def percent_of_references_with_a_hash(self):
        if self.number_of_references == 0:
            return 0
        else:
            return int(
                self.number_of_hashed_references * 100 / self.number_of_references
            )

    @property
    def underscored_title(self):
        """Helper property"""
        if self.title is None:
            raise ValueError("self.title was None")
        return self.title.replace(" ", "_")

    @property
    def url(self):
        return (
            f"https://{self.language_code}.{self.wikimedia_site.value}.org/"
            f"wiki/{self.underscored_title}"
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
        if config.use_cache:
            wcdqid = self.__get_wcdqid_from_cache__(reference=reference)
            if wcdqid is not None:
                logger.debug(f"Got wcdqid:{wcdqid} from the cache")
                reference.wikicitations_qid = wcdqid
            else:
                reference = (
                    self.__upload_reference_and_insert_in_the_cache_if_enabled__(
                        reference=reference
                    )
                )
        else:
            wcdqid = self.__get_wcdqid_from_hash_via_sparql__(reference=reference)
            if wcdqid is not None:
                logger.debug(f"Got wcdqid:{wcdqid} from the cache")
                reference.wikicitations_qid = wcdqid
            else:
                reference = (
                    self.__upload_reference_and_insert_in_the_cache_if_enabled__(
                        reference=reference
                    )
                )
        return reference

    @validate_arguments
    def __get_wcdqid_from_hash_via_sparql__(self, md5hash: str) -> Optional[str]:
        """Looks up the WCDQID in WikiCitaitons and returns
        it if only one found and complains if more than one was"""
        logger.info("Looking up the WCDQID via SPARQL")
        if self.wikicitations is None:
            from src import WikiCitations

            self.wikicitations = WikiCitations()
        if self.wikicitations is not None:
            wcdqids = self.wikicitations.__get_wcdqids_from_hash__(md5hash=md5hash)
            if wcdqids is not None:
                if len(wcdqids) > 1:
                    raise ValueError(
                        "Got more than one WCDQID for a hash. This should never happen"
                    )
                elif len(wcdqids) == 1:
                    return wcdqids[0]

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
        self.__parse_templates__()
        self.__print_hash_statistics__()

    @validate_arguments
    def __fetch_page_data__(self, title: str) -> str:
        """This fetches metadata and the latest revision id
        and date from the MediaWiki REST v1 API"""
        self.title = title
        url = f"https://en.wikipedia.org/w/rest.php/v1/page/{title}"
        headers = {"User-Agent": config.user_agent}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # TODO read up on the documentation to find out if this is reliable
            self.latest_revision_id = int(data["latest"]["id"])
            self.latest_revision_date = isoparse(data["latest"]["timestamp"])
            self.page_id = int(data["id"])
            self.wikitext = data["source"]
        else:
            raise ValueError(
                f"Could not fetch page data. Got {response.status_code} from {url}"
            )

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

    @validate_arguments
    def __get_wcdqid_from_cache__(
        self, reference: WikipediaPageReference
    ) -> Optional[str]:
        if self.cache is None:
            self.__setup_cache__()
        wcdqid = self.cache.check_reference_and_get_wikicitations_qid(
            reference=reference
        )
        logger.debug(f"result from the cache:{wcdqid}")
        return wcdqid

    @validate_arguments
    def __get_wikipedia_page_from_title__(self, title: str):
        """Get the page from the Wikimedia site"""
        logger.info("Fetching the page data")
        self.__fetch_page_data__(title=title)

    @validate_arguments
    def __insert_in_cache__(self, reference: WikipediaPageReference, wcdqid: str):
        logger.debug("__insert_in_cache__: Running")
        self.cache.add_reference(reference=reference, wcdqid=wcdqid)
        logger.info("Reference inserted into the hash database")

    def __page_has_already_been_uploaded__(self) -> bool:
        """This checks whether the page has already been uploaded by checking the cache"""
        if config.use_cache:
            if self.cache is None:
                self.__setup_cache__()
            if self.cache is not None:
                wcdqid = self.cache.check_page_and_get_wikicitations_qid(
                    wikipedia_page=self
                )
            else:
                raise ValueError("self.cache was None")
            if wcdqid is None:
                logger.debug("Page not found in the cache")
                return False
            else:
                logger.debug("Page found in the cache")
                return True
        else:
            # Fallback
            logger.info("Not using the cache. Falling back to lookup via SPARQL")
            if self.md5hash is not None:
                wcdqid = self.__get_wcdqid_from_hash_via_sparql__(md5hash=self.md5hash)
            else:
                raise ValueError("self.md5hash was None")
            if wcdqid is not None:
                self.wikicitations_qid = wcdqid
                return True
            else:
                return False

    def __parse_templates__(self):
        """We parse all the templates into WikipediaPageReferences"""
        if self.wikitext is None:
            raise ValueError("self.wikitext was None")
        # We use the pywikibot template extracting function
        template_tuples = extract_templates_and_params(self.wikitext, True)
        number_of_templates = len(template_tuples)
        logger.info(
            f"Parsing {number_of_templates} templates from {self.title}, see {self.url}"
        )
        self.references = []
        for template_name, content in template_tuples:
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

    def __print_hash_statistics__(self):
        logger.info(
            f"Hashed {self.percent_of_references_with_a_hash} percent of "
            f"{len(self.references)} references on page {self.title}"
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
        if self.wikicitations is not None:
            wcdqid = self.wikicitations.prepare_and_upload_reference_item(
                page_reference=reference, wikipedia_page=self
            )
        else:
            raise ValueError("self.wikicitations was None")
        if wcdqid is None:
            raise ValueError(
                "Got None instead of WCDQID when trying to upload to WikiCitations"
            )
        return wcdqid

    @validate_arguments
    def __upload_reference_and_insert_in_the_cache_if_enabled__(
        self, reference: WikipediaPageReference
    ):
        # Here we get the reference back with WCDQID
        wcdqid = self.__upload_reference_to_wikicitations__(reference=reference)
        if config.use_cache:
            if wcdqid is None:
                raise ValueError("WCDQID was None")
            if reference.md5hash is None:
                raise ValueError("hash was None")
            logger.debug(
                f"Hash before insertion: {reference.md5hash}. "
                f"WCDQID before insertion: {wcdqid}"
            )
            self.__insert_in_cache__(reference=reference, wcdqid=wcdqid)
            reference.wikicitations_qid = wcdqid
        return reference

    def __upload_references_if_missing__(self):
        """Go through each reference and upload if missing to WikiCitations"""
        updated_references = []
        for reference in self.references:
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
        if not self.__page_has_already_been_uploaded__():
            logger.info("This page is missing from WikiCitations")
            self.__setup_wikicitations__()
            self.__fetch_page_data__(title=self.title)
            # extract references and create items for the missing ones first
            self.__extract_and_parse_references__()
            self.__upload_references_if_missing__()
            # upload a new item for the page with links to all the page_reference items
            wcdqid = self.wikicitations.prepare_and_upload_wikipedia_page_item(
                wikipedia_page=self,
            )
            if config.use_cache:
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
    #     logger.info("Fetching the parsed_wikitext")
    #     self.pywikibot_page = pywikibot.Page(
    #         self.wikimedia_event.event_stream.pywikibot_site, self.title
    #     )
