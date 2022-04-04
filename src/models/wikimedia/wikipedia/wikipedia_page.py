from __future__ import annotations

import json
import logging
from typing import List, Any, Optional, Dict

import pywikibot  # type: ignore
from pydantic import BaseModel, validate_arguments
from pywikibot import Page, Site

import config
from src import WikimediaSite, console, Cache
from src.models.wikimedia.wikipedia.templates.english_wikipedia_page_reference import (
    EnglishWikipediaPageReferenceSchema,
    EnglishWikipediaPageReference,
)
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

logger = logging.getLogger(__name__)


class WikipediaPage(BaseModel):
    """Models a WMF Wikipedia page"""

    cache: Optional[Cache]
    language_code: str = "en"
    md5hash: Optional[str]
    # number_of_references_without_a_hash: Optional[int]
    # percent_of_references_missing_a_hash: Optional[int]
    percent_of_references_with_a_hash: Optional[int]
    pywikibot_page: Optional[Page]
    pywikibot_site: Optional[Any]
    references: Optional[List[WikipediaPageReference]]
    # references_without_hashes: Optional[List[WikipediaPageReference]]
    wikicitations: Optional[Any]  # This is needed
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
    def title(self):
        """Helper property"""
        return str(self.pywikibot_page.title)

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
    def __check_and_upload_reference_item_if_missing__(
        self, reference: WikipediaPageReference
    ):
        if config.use_cache is not None:
            wcdqid = self.__get_wcdqid_from_cache__(reference=reference)
            if wcdqid:
                reference.wikicitations_qid = wcdqid
            else:
                reference = self.__upload_reference_to_wikicitations__(
                    reference=reference
                )
                self.__insert_in_cache__(reference=reference)
        return reference

    def __extract_references__(self):
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

    def __fix_keys__(self, dictionary: Dict[str, Any]) -> Dict[str, Any]:
        dictionary = self.__fix_class_key__(dictionary=dictionary)
        dictionary = self.__fix_aliases__(dictionary=dictionary)
        return self.__fix_dash__(dictionary=dictionary)

    # def __get_title_from_event__(self):
    #     self.title = self.wikimedia_event.page_title
    #     if self.title is None or self.title == "":
    #         raise ValueError("title not set correctly")

    def __get_wcdqid_from_cache__(self, reference: WikipediaPageReference):
        if self.cache is None:
            self.__setup_cache__()
        wcdqid = self.cache.check_reference_and_get_wikicitations_qid(
            reference=reference
        )
        print(f"result:{wcdqid}")
        return wcdqid

    # def __get_wikipedia_page_from_event__(self):
    #     """Get the page from Wikipedia"""
    #     logger.info("Fetching the wikitext")
    #     self.pywikibot_page = pywikibot.Page(
    #         self.wikimedia_event.event_stream.pywikibot_site, self.title
    #     )

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

    def __insert_in_cache__(self, reference: WikipediaPageReference):
        self.cache.add_reference(reference=reference)
        logger.info("Reference inserted into the hash database")

    def __parse_templates__(self, check_and_upload_to_cache: bool = True):
        """We parse all the templates into WikipediaPageReferences"""
        raw = self.pywikibot_page.raw_extracted_templates
        number_of_templates = len(raw)
        logger.info(
            f"Parsing {number_of_templates} templates from {self.pywikibot_page.title()}, see {self.url}"
        )
        self.references = []
        supported_templates = [
            "citation",  # see https://en.wikipedia.org/wiki/Template:Citation
            "cite q",
            "citeq",
            "isbn",
            "url",
            # CS1 templates:
            "cite arxiv",
            "cite av media notes",
            "cite av media",
            "cite biorxiv",
            "cite book",
            "cite cite seerx",
            "cite conference",
            "cite encyclopedia",
            "cite episode",
            "cite interview",
            "cite journal",
            "cite magazine",
            "cite mailing list" "cite map",
            "cite news",
            "cite newsgroup",
            "cite podcast",
            "cite press release",
            "cite report",
            "cite serial",
            "cite sign",
            "cite speech",
            "cite ssrn",
            "cite techreport",
            "cite thesis",
            "cite web",
        ]
        for template_name, content in raw:
            # logger.debug(f"working on {template_name}")
            if template_name.lower() in supported_templates:
                parsed_template = self.__fix_keys__(json.loads(json.dumps(content)))
                parsed_template["template_name"] = template_name.lower()
                logger.debug(parsed_template)
                schema = EnglishWikipediaPageReferenceSchema()
                reference: EnglishWikipediaPageReference = schema.load(parsed_template)
                reference.parse_persons()
                reference.parse_isbn()
                reference.generate_hash()
                if check_and_upload_to_cache and reference.has_hash:
                    reference = self.__check_and_upload_reference_item_if_missing__(
                        reference=reference
                    )
                if config.loglevel == logging.DEBUG:
                    console.print(reference.dict())
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

        self.wikicitations = WikiCitations()

    @validate_arguments
    def __upload_reference_to_wikicitations__(
        self, reference: WikipediaPageReference
    ) -> WikipediaPageReference:
        if self.wikicitations is None:
            self.__setup_wikicitations__()
        reference.wikicitations_qid = (
            self.wikicitations.prepare_and_upload_reference_item(
                page_reference=reference, wikipedia_page=self
            )
        )
        if reference.wikicitations_qid is None:
            raise ValueError(
                "Got None instead of WCDQID when trying to upload to WikiCitations"
            )
        return reference

    def extract_and_upload_to_wikicitations(self):
        self.__setup_wikicitations__()
        # extract references and create items for the missing ones first
        self.__extract_references__()
        # upload a new item for the page with links to all the page_reference items
        self.wikicitations.prepare_and_upload_wikipedia_page_item(wikipedia_page=self)

    def export_to_dataframe(self):
        # TODO make it easy to quantify the references with pandas
        raise NotImplementedError("To be written")

    # def __match_subjects__(self):
    #     logger.info(f"Matching subjects from {len(self.dois) - self.number_of_missing_dois} DOIs")
    #     [doi.wikidata_scientific_item.crossref_engine.work.match_subjects_to_qids() for doi in self.dois
    #      if (
    #              doi.wikidata_scientific_item.doi_found_in_wikidata and
    #              doi.wikidata_scientific_item.crossref_engine is not None and
    #              doi.wikidata_scientific_item.crossref_engine.work is not None
    #      )]
