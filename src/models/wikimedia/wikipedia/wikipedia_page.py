from __future__ import annotations

import json
import logging
from typing import List, Any, TYPE_CHECKING, Optional

import pywikibot  # type: ignore
from pydantic import BaseModel
from pywikibot import Page

from src.models.wikimedia.wikipedia.templates.enwp.cite_book import CiteBook
from src.models.wikimedia.wikipedia.templates.enwp.cite_journal import CiteJournal
from src.models.wikimedia.wikipedia.templates.enwp.cite_news import CiteNews
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import WikipediaPageReference

if TYPE_CHECKING:
    from src.models.identifier.doi import Doi

logger = logging.getLogger(__name__)


# This is a hack. Copying it here avoids an otherwise seemingly unavoidable cascade of pydantic errors...


class WikipediaPage(BaseModel):
    """Models a WMF Wikipedia page"""
    pywikibot_page: Optional[Page] = None
    dois: Optional[List[Doi]] = None
    missing_dois: Optional[List[Doi]] = None
    number_of_dois: int = 0
    number_of_isbns: int = 0
    number_of_missing_dois: int = 0
    number_of_missing_isbns: int = 0
    page_id: Optional[int] = None
    references: Optional[List[WikipediaPageReference]] = None
    title: Optional[str] = None
    # We can't type this with WikimediaEvent because of pydantic
    wikimedia_event: Optional[Any]
    pywikibot_site: Optional[Any]

    class Config:
        arbitrary_types_allowed = True

    def __calculate_statistics__(self):
        self.number_of_dois = len(self.dois)
        self.number_of_missing_dois = len(self.missing_dois)
        logger.info(f"{self.number_of_missing_dois} out of {self.number_of_dois} "
                    f"DOIs on this page were missing in Wikidata")
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

    def __get_title_from_event__(self):
        self.title = self.wikimedia_event.page_title
        if self.title is None or self.title == "":
            raise ValueError("title not set correctly")

    def __get_wikipedia_page_from_event__(self):
        """Get the page from Wikipedia"""
        logger.info("Fetching the wikitext")
        self.pywikibot_page = pywikibot.Page(self.wikimedia_event.event_stream.pywikibot_site, self.title)
        # this id is useful when talking to WikipediaCitations because it is unique
        self.page_id = int(self.pywikibot_page.pageid)

    def __get_wikipedia_page_from_title__(self):
        """Get the page from Wikipedia"""
        logger.info("Fetching the wikitext")
        self.pywikibot_page = pywikibot.Page(self.pywikibot_site, self.title)
        # this id is useful when talking to WikipediaCitations because it is unique
        self.page_id = int(self.pywikibot_page.pageid)

    # def __match_subjects__(self):
    #     logger.info(f"Matching subjects from {len(self.dois) - self.number_of_missing_dois} DOIs")
    #     [doi.wikidata_scientific_item.crossref_engine.work.match_subjects_to_qids() for doi in self.dois
    #      if (
    #              doi.wikidata_scientific_item.doi_found_in_wikidata and
    #              doi.wikidata_scientific_item.crossref_engine is not None and
    #              doi.wikidata_scientific_item.crossref_engine.work is not None
    #      )]

    def __parse_templates__(self):
        """We parse all the templates into WikipediaPageReferences"""
        logger.info("Parsing templates")
        raw = self.pywikibot_page.raw_extracted_templates
        self.references = []
        self.dois = []
        for template_name, content in raw:
            # logger.debug(f"working on {template_name}")
            if template_name.lower() == "cite journal":
                # Workaround from https://stackoverflow.com/questions/56494304/how-can-i-do-to-convert-ordereddict-to
                # -dict First we convert the list of tuples to a normal dict
                content_as_dict = json.loads(json.dumps(content))
                # Then we add the dict to the "doi" key that pydantic expects
                # logger.debug(f"content_dict:{content_as_dict}")
                # if "doi" in content_as_dict:
                #     doi = content_as_dict["doi"]
                #     content_as_dict["doi"] = dict(
                #         value=doi
                #     )
                # else:
                #     content_as_dict["doi"] = None
                cite_journal = CiteJournal(**content_as_dict)
                self.references.append(cite_journal)
                if cite_journal.doi is not None:
                    from src.models.identifier.doi import Doi
                    doi = Doi(value=cite_journal.doi)
                    doi.__test_doi__()
                    if doi.regex_validated:
                        self.number_of_dois += 1
                        self.dois.append(doi)
                else:
                    # We ignore cultural magazines for now
                    if cite_journal.journal_title is not None and "magazine" not in cite_journal.journal_title:
                        logger.warning(f"An article titled {cite_journal.title} "
                                       f"in the journal_title {cite_journal.journal_title} "
                                       f"was found but no DOI. "
                                       f"(pmid:{cite_journal.pmid} jstor:{cite_journal.jstor})")
        # exit()
            if template_name.lower() == "cite news":
                reference = CiteNews(**json.loads(json.dumps(content)))
                self.references.append(reference)
            if template_name.lower() == "cite book":
                reference = CiteBook(**json.loads(json.dumps(content)))
                self.references.append(reference)