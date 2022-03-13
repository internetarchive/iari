from __future__ import annotations

import json
import logging
from typing import List, Any, TYPE_CHECKING, Optional, Dict

import pywikibot  # type: ignore
from pydantic import BaseModel
from pywikibot import Page

from src import WikimediaSite
from src.models.wikimedia.wikipedia.templates.enwp import EnglishWikipediaPageReference
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

if TYPE_CHECKING:
    from src.models.identifier.doi import Doi

logger = logging.getLogger(__name__)


# This is a hack. Copying it here avoids an otherwise seemingly unavoidable cascade of pydantic errors...


class WikipediaPage(BaseModel):
    """Models a WMF Wikipedia page"""

    language_code: str
    pywikibot_page: Optional[Page]
    pywikibot_site: Optional[Any]
    references: Optional[List[WikipediaPageReference]]
    title: Optional[str]
    wikimedia_event: Optional[
        Any  # We can't type this with WikimediaEvent because of pydantic
    ]
    wikimedia_site: WikimediaSite

    class Config:
        arbitrary_types_allowed = True

    @property
    def url(self):
        return (
            f"https://{self.language_code}.{self.wikimedia_site.value}.org/"
            f"wiki/{self.pywikibot_page.title(underscore=True)}"
        )

    def __calculate_statistics__(self):
        self.number_of_dois = len(self.dois)
        self.number_of_missing_dois = len(self.missing_dois)
        logger.info(
            f"{self.number_of_missing_dois} out of {self.number_of_dois} "
            f"DOIs on this page were missing in Wikidata"
        )
        # if len(missing_dois) > 0:
        #     input_output.save_to_wikipedia_list(missing_dois, language_code, title)
        # if config.import_mode:
        # answer = util.yes_no_question(
        #     f"{doi} is missing in WD. Do you"+
        #     " want to add it now?"
        # )
        # if answer:
        #     crossref_engine.lookup_data(doi=doi, in_wikipedia=True)
        #     pass
        # else:
        #     pass

    def __get_title_from_event__(self):
        self.title = self.wikimedia_event.page_title
        if self.title is None or self.title == "":
            raise ValueError("title not set correctly")

    def __get_wikipedia_page_from_event__(self):
        """Get the page from Wikipedia"""
        logger.info("Fetching the wikitext")
        self.pywikibot_page = pywikibot.Page(
            self.wikimedia_event.event_stream.pywikibot_site, self.title
        )
        # this id is useful when talking to WikipediaCitations because it is unique
        self.page_id = int(self.pywikibot_page.pageid)

    def __get_wikipedia_page_from_title__(self):
        """Get the page from Wikipedia"""
        logger.info("Fetching the wikitext")
        self.pywikibot_page = pywikibot.Page(self.pywikibot_site, self.title)
        # this id is useful when talking to WikipediaCitations because it is unique
        # self.page_id = int(self.pywikibot_page.pageid)

    # def __match_subjects__(self):
    #     logger.info(f"Matching subjects from {len(self.dois) - self.number_of_missing_dois} DOIs")
    #     [doi.wikidata_scientific_item.crossref_engine.work.match_subjects_to_qids() for doi in self.dois
    #      if (
    #              doi.wikidata_scientific_item.doi_found_in_wikidata and
    #              doi.wikidata_scientific_item.crossref_engine is not None and
    #              doi.wikidata_scientific_item.crossref_engine.work is not None
    #      )]
    def __fix_class_key__(self, dict) -> Dict[str, Any]:
        """convert "class" key to "_class" to avoid collision with reserved python expression"""
        newdict = {}
        for key in dict:
            if key == "class":
                new_key = "news_class"
            newdict[new_key] = dict[key]
        return newdict

    def __parse_templates__(self):
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
                parsed_template = self.__fix_class_key__(
                    json.loads(json.dumps(content))
                )
                parsed_template["template_name"] = template_name.lower()
                reference = EnglishWikipediaPageReference(**parsed_template)
                self.references.append(reference)
            else:
                logger.warning(f"Template '{template_name.lower()}' not supported")

    def extract_references(self):
        if self.wikimedia_event is not None:
            # raise ValueError("wikimedia_event was None")
            self.__get_title_from_event__()
            self.__get_wikipedia_page_from_event__()
        elif self.title is not None:
            if self.pywikibot_site is None:
                raise ValueError("self.pywikibot_site was None")
            self.__get_wikipedia_page_from_title__()
        else:
            if self.pywikibot_page is None:
                raise ValueError("self.pywikibot_page was None")
        self.__parse_templates__()
