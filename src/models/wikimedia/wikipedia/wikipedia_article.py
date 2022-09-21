from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
from dateutil.parser import isoparse
from marshmallow.exceptions import ValidationError
from pydantic import validate_arguments

import config
from src.helpers import console
from src.helpers.template_extraction import extract_templates_and_params
from src.models.exceptions import MissingInformationError, WikibaseError
from src.models.return_.wikibase_return import WikibaseReturn
from src.models.wcd_item import WcdItem
from src.models.wikibase.website import Website
from src.models.wikimedia.enums import WikimediaSite
from src.models.wikimedia.wikipedia.references.english_wikipedia import (
    EnglishWikipediaPageReferenceSchema,
)
from src.models.wikimedia.wikipedia.references.wikipedia import WikipediaReference

logger = logging.getLogger(__name__)


class WikipediaArticle(WcdItem):
    """Models a WMF Wikipedia page"""

    latest_revision_date: Optional[datetime]
    latest_revision_id: Optional[int]
    md5hash: Optional[str]
    page_id: Optional[int]
    references: List[WikipediaReference] = []
    wikimedia_event: Optional[
        Any  # We can't type this with WikimediaEvent because of pydantic
    ]
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA
    wikitext: Optional[str]

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
    def is_redirect(self) -> bool:
        if "#REDIRECT" in str(self.wikitext)[:10]:
            return True
        else:
            return False

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
            f"wiki/{quote(self.underscored_title)}"
        )

    @property
    def wikibase_url(self):
        if self.wikibase.item_prefixed_wikibase:
            return f"{self.wikibase.wikibase_url}wiki/Item:{self.return_.item_qid}"
        else:
            return f"{self.wikibase.wikibase_url}wiki/{self.return_.item_qid}"

    def __calculate_hashed_template_distribution__(self):
        raise NotImplementedError("To be written")

    def __compare_and_update_all_references__(self) -> None:
        """Compare and update all the references.
        We assume all references have already been uploaded to Wikibase"""
        logger.debug("__compare_and_update_all_references__: Running")
        if not self.references:
            console.print("No references found. Skipping comparison of references")
            # raise MissingInformationError("self.references was empty or None")
        else:
            self.__setup_wikibase_crud_update__(wikipedia_article=self)
            if self.wikibase_crud_update:
                count = 0
                total = len(self.references)
                for reference in self.references:
                    """We go through each reference that has a hash
                    and compare it to the existing one in Wikibase"""
                    if reference.has_hash:
                        if not reference.return_:
                            logger.debug(f"reference: {reference}")
                            raise MissingInformationError(
                                "reference.return_ was None and is needed "
                                f"to judge whether to compare or not"
                            )
                        count += 1
                        console.print(
                            f"Comparing reference {count}/{total} on page '{self.title}'"
                        )
                        self.wikibase_crud_update.compare_and_update_claims(
                            entity=reference
                        )
            else:
                raise WikibaseError()

    def __compare_and_update_page__(self):
        logger.debug("__compare_and_update_page__: Running")
        console.print(f"Comparing the page '{self.title}'")
        if not self.return_:
            raise MissingInformationError(
                "self.return_ was None and is needed "
                "to judge whether to compare or not"
            )
        self.__setup_wikibase_crud_update__(wikipedia_article=self)
        self.wikibase_crud_update.compare_and_update_claims(entity=self)

    def __compare_data_and_update__(self):
        """We compare and update all references and the page data"""
        logger.debug("__compare_data_and_update__: Running")
        if config.compare_references:
            self.__compare_and_update_all_references__()
        self.__compare_and_update_page__()

    def __extract_and_parse_references__(self):
        logger.info("Extracting references now")
        # if self.wikimedia_event is not None:
        #     # raise ValueError("wikimedia_event was None")
        #     self.__get_title_from_event__()
        #     self.__get_wikipedia_page_from_event__()
        # elif self.title is not None:
        #     if self.pywikibot_site is None:
        #         raise ValueError("self.pywikibot_site was None")
        #     self.__get_wikipedia_article_from_title__()
        # else:
        self.__parse_templates__()
        self.__print_hash_statistics__()

    def __fetch_page_data__(self, title: str = "") -> None:
        """This fetches metadata and the latest revision id
        and date from the MediaWiki REST v1 API if needed"""
        # TODO refactor this into new class?
        logger.debug("__fetch_page_data__: Running")
        if (
            not self.latest_revision_id
            or not self.latest_revision_date
            or not self.wikitext
            or not self.page_id
        ):
            if not title and self.title:
                title = self.title
            elif not title and not self.title:
                raise MissingInformationError(
                    "Both self.title and title are empty or None"
                )
            else:
                self.title = title
            # This is needed to support e.g. https://en.wikipedia.org/wiki/Musk%C3%B6_naval_base
            title = title.replace(" ", "_")
            # TODO avoid hard coding here
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
        else:
            logger.debug(
                "Not fetching via REST API. We have already got all the data we need"
            )

    def __fetch_wikidata_qid__(self):
        """Fetch the Wikidata QID so we can efficiently look up pages via JS"""
        # TODO avoid hard coding here
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&redirects=1&titles={quote(self.title)}&format=json"
        headers = {"User-Agent": config.user_agent}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # console.print(response.text)
            data = response.json()
            # console.print(data)
            query = data.get("query")
            if query:
                pages = query.get("pages")
                if pages:
                    if len(pages):
                        for page in pages:
                            page_data = pages[page]
                            # console.print(page_data)
                            self.wikidata_qid = page_data["pageprops"]["wikibase_item"]
                            # We only care about the first page
                            break
                    else:
                        raise MissingInformationError(
                            f"Did not get any pages from MediaWiki, see {url}"
                        )
                else:
                    raise MissingInformationError(
                        f"Did not get any pages-key from MediaWiki, see {url}"
                    )
            else:
                raise MissingInformationError(
                    f"Did not get any query from MediaWiki, see {url}"
                )
            logger.info(f"Found Wikidata QID: {self.wikidata_qid}")

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

    @validate_arguments
    def __fix_keys__(self, dictionary: Dict[str, Any]) -> Dict[str, Any]:
        dictionary = self.__fix_class_key__(dictionary=dictionary)
        dictionary = self.__fix_aliases__(dictionary=dictionary)
        return self.__fix_dash__(dictionary=dictionary)

    def __generate_hash__(self):
        """We generate a md5 hash of the page_reference as a unique identifier for any given page_reference in a Wikipedia page
        We choose md5 because it is fast https://www.geeksforgeeks.org/difference-between-md5-and-sha1/"""
        logger.debug(
            f"Generating hash based on: "
            f"{self.wikibase.title}{self.language_code}{self.page_id}"
        )
        if not self.page_id:
            raise MissingInformationError("self.page_id was None")
        self.md5hash = hashlib.md5(
            f"{self.wikibase.title}{self.language_code}{self.page_id}".encode()
        ).hexdigest()
        logger.debug(self.md5hash)

    @validate_arguments
    def __get_wikipedia_article_from_title__(self, title: str):
        """Get the page from the Wikimedia site"""
        logger.info("Fetching the page data")
        self.__fetch_page_data__(title=title)

    def __page_has_already_been_uploaded__(self) -> bool:
        """This checks whether the page has already been uploaded by checking the cache"""
        console.print(f"Checking if the page '{self.title}' has already been uploaded")
        if self.cache is None:
            self.__setup_cache__()
        if self.cache is not None:
            cache_return = self.cache.check_page_and_get_wikibase_qid(
                wikipedia_article=self
            )
        else:
            raise ValueError("self.cache was None")
        if not cache_return.item_qid:
            logger.debug("Page not found in the cache")
            return False
        else:
            logger.debug("Page found in the cache")
            self.return_ = WikibaseReturn(
                item_qid=cache_return.item_qid, uploaded_now=False
            )
            return True

    def __parse_templates__(self):
        """We parse all the references into WikipediaPageReferences"""
        if self.wikitext is None:
            raise ValueError("self.wikitext was None")
        # We use the pywikibot template extracting function
        template_tuples = extract_templates_and_params(self.wikitext, True)
        number_of_templates = len(template_tuples)
        logger.info(
            f"Parsing {number_of_templates} references from {self.title}, see {self.url}"
        )
        for template_name, content in template_tuples:
            # logger.debug(f"working on {template_name}")
            if template_name.lower() in config.supported_templates:
                parsed_template = self.__fix_keys__(json.loads(json.dumps(content)))
                parsed_template["template_name"] = template_name.lower()
                if config.loglevel == logging.DEBUG:
                    logger.debug("parsed_template:")
                    console.print(parsed_template)
                    # press_enter_to_continue()
                schema = EnglishWikipediaPageReferenceSchema()
                try:
                    reference: Optional[WikipediaReference] = schema.load(
                        parsed_template
                    )
                except ValidationError as error:
                    logger.debug(f"Validation error: {error}")
                    schema_log_file = "schema_errors.log"
                    self.__log_to_file__(message=str(error), file_name=schema_log_file)
                    logger.error(
                        f"This reference was skipped because an unknown "
                        f"field was found. See the file '{schema_log_file}' for details"
                    )
                    reference = None
                # DISABLED partial loading because it does not work :/
                # if not reference:
                #     logger.info("Trying now to deserialize the reference partially")
                #     # Load partially (ie. ignore the unknown field)
                #     reference: WikipediaReference = schema.load(
                #         parsed_template, partial=True
                #     )
                # if not reference:
                #     raise ValueError("This reference could not be deserialized. :/")
                # else:
                if reference:
                    reference.wikibase = self.wikibase
                    reference.finish_parsing_and_generate_hash()
                    # Handle duplicates:
                    if reference.md5hash in [
                        reference.md5hash
                        for reference in self.references
                        if reference.md5hash is not None
                    ]:
                        logging.debug(
                            "Skipping reference already present "
                            "in the list to avoid duplicates"
                        )
                    # if config.loglevel == logging.DEBUG:
                    #     console.print(reference.dict())
                    else:
                        self.references.append(reference)
            else:
                if config.debug_unsupported_templates:
                    logger.debug(f"Template '{template_name.lower()}' not supported")

    def __print_hash_statistics__(self):
        logger.info(
            f"Hashed {self.percent_of_references_with_a_hash} percent of "
            f"{len(self.references)} references on page {self.title}"
        )

    def __upload_page_and_references__(self):
        console.print(f"Importing page '{self.title}'")
        self.__setup_wikibase_crud_create__()
        self.return_ = (
            self.wikibase_crud_create.prepare_and_upload_wikipedia_article_item(
                wikipedia_article=self,
            )
        )
        if self.return_ is None:
            raise ValueError("wcdqid was None")
        self.cache.add_page(wikipedia_article=self, wcdqid=self.return_.item_qid)
        if self.return_.uploaded_now:
            console.print(
                f"Finished uploading {self.title} to Wikibase, "
                f"see {self.url} and {self.wikibase_url}"
            )
        else:
            # This branch is hit e.g. when the cache has not been synced with the wikibase
            console.print(
                f"{self.title} already exists in {self.wikibase.__repr_name__()}, "
                f"see {self.url} and {self.wikibase_url}. \nPlease run the bot with --rebuild-cache "
                f"to speed up the process."
            )
            self.__compare_data_and_update__()

    def __upload_references_and_websites_if_missing__(self):
        """Go through each reference and upload if missing to Wikibase"""
        logger.debug("__upload_references_and_websites_if_missing__: Running")
        updated_references = []
        count = 1
        total = len(self.references)
        for reference in self.references:
            console.print(f"Working on reference {count}/{total}")
            # Here we check for an existing website item
            if reference.has_first_level_domain_url_hash:
                with console.status(
                    f"Linking to or uploading new website item for reference "
                    f"with link to {reference.first_level_domain_of_url}"
                ):
                    # Here we get the reference with the first_level_domain_of_url WCDQID back
                    reference.website_item = Website(
                        reference=reference, wikibase=self.wikibase
                    )
                    reference.website_item.check_and_upload_website_item_to_wikibase_if_missing(
                        wikipedia_article=self
                    )
            # Here we check for an existing reference item
            if reference.has_hash:
                with console.status(f"Creating the reference item if missing"):
                    # Here we get the reference with WikibaseReturn back
                    reference.check_and_upload_reference_item_to_wikibase_if_missing()
                    if not reference.return_:
                        raise MissingInformationError(
                            "reference.return_ was None and is needed "
                            "to judge whether to compare or not"
                        )
            updated_references.append(reference)
            count += 1
        self.references = updated_references

    def extract_and_parse_and_upload_missing_items_to_wikibase(self) -> None:
        """Extract the references and upload first
        the references and then the page to Wikibase

        First we fetch the page data and generate the hash,
        then we setup the Wikibase and extract and parse
        the references.

        Then we upload the references and websites if missing
        and lastly we either upload the page or if missing
        compare and upload any missing claims."""
        logger.debug("extract_and_upload_to_wikibase: Running")
        self.__fetch_page_data__()
        if not self.is_redirect:
            self.__fetch_wikidata_qid__()
            self.__generate_hash__()
            self.__setup_wikibase_crud_create__()
            self.__extract_and_parse_references__()
            self.__upload_references_and_websites_if_missing__()
            if not self.__page_has_already_been_uploaded__():
                self.__upload_page_and_references__()
            else:
                self.__compare_data_and_update__()
        else:
            console.print("This page is a redirect to another page. Not importing.")

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
