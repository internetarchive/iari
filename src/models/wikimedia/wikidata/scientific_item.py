import logging
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import quote

import requests
from wikibaseintegrator import wbi_login, wbi_config, WikibaseIntegrator  # type: ignore
from wikibaseintegrator.datatypes import Time, Item as WbiItemType, String  # type: ignore
from wikibaseintegrator.entities.item import Item as WbiEntityItem  # type: ignore
from wikibaseintegrator.wbi_enums import ActionIfExists  # type: ignore

import src.runtime_variables
import config
from src.models.crossref_engine.ontology_based_ner_matcher import FuzzyMatch
from src.helpers.console import console
from src.models.crossref_engine import CrossrefEngine
from src.models.pickled_dataframe.statistics import Statistics
from src.models.wikimedia.enums import StatedIn, Property, DeterminationMethod
from src.models.wikimedia.wikidata.entity_id import EntityId
from src.models.wikimedia.wikidata.item import Item

logger = logging.getLogger(__name__)


class WikidataScientificItem(Item):
    """This models a scientific item on Wikidata

    We get data on init, because getting a Doi object leads to circular dependency issues"""
    crossref: Optional[CrossrefEngine] = None
    crossref_doi: Optional[str] = None
    doi_found_in_crossref: bool = False
    doi_found_in_wikidata: bool = False
    wikipedia_doi: str  # This is mandatory

    # TODO factor out to own class
    def __call_the_hub_api__(self, doi: str = None):
        if doi is None:
            raise ValueError("doi was None")
        if doi == "":
            logger.warning("doi was empty string")
        else:
            url = f"https://hub.toolforge.org/doi:{quote(doi)}?site=wikidata?format=json"
            response = requests.get(url, allow_redirects=False)
            if response.status_code == 302:
                location = response.headers['Location']
                if config.loglevel == logging.DEBUG:
                    console.print(f"[bold red]location from hub: {location}[/bold red]")
                if config.wikidata_wiki_prefix in location:
                    logger.debug("Found QID via Hub")
                    self.doi_found_in_wikidata = True
                    self.qid = EntityId(raw_identifier=location)
                else:
                    logger.error(f"Got {location} from Hub instead of a QID")
                    self.doi_found_in_wikidata = False
            elif response.status_code == 400:
                self.doi_found_in_wikidata = False
            else:
                logger.error(f"Got {response.status_code} from Hub")
                console.print(response.json())
                exit(0)

    def __lookup_in_crossref__(self):
        """Lookup in CrossrefEngine and parse the whole result into an object we can use"""
        logger.debug(f"Looking up {self.wikipedia_doi} in CrossrefEngine")
        self.crossref = CrossrefEngine(wikipedia_doi=self.wikipedia_doi)
        self.crossref.lookup_work()
        if self.crossref.work is not None:
            # This helps us easily in WikipediaPage to get an overview
            self.doi_found_in_crossref = True
        else:
            self.doi_found_in_crossref = False

    def __lookup_via_hub__(self) -> None:
        """Lookup via hub.toolforge.org using the DOI from CrossrefEngine if possible
        It is way faster than WDQS
        https://hub.toolforge.org/doi:10.1111/j.1746-8361.1978.tb01321.x?site:wikidata?format=json"""
        logger.info("Looking up via Hub")
        if self.crossref_doi:
            if self.crossref_doi == "":
                logger.warning("doi from crossref_engine was empty string")
            else:
                logger.debug("Using DOI from CrossrefEngine to lookup in Hub")
                self.__call_the_hub_api__(self.crossref_doi)
        if not self.doi_found_in_wikidata:
            logger.debug("Using DOI from Wikipedia to lookup in Hub")
            self.__call_the_hub_api__(self.wikipedia_doi)
            if not self.doi_found_in_wikidata:
                logger.debug("Using uppercase DOI from Wikipedia to lookup in Hub")
                self.__call_the_hub_api__(self.wikipedia_doi.upper())
                if not self.doi_found_in_wikidata:
                    logger.debug("Using lowercase DOI from Wikipedia to lookup in Hub")
                    self.__call_the_hub_api__(self.wikipedia_doi.lower())

    def __upload_main_subject_using_wbi__(
            self,
            match: FuzzyMatch
    ) -> None:
        """This adds a main subject to the item

        It only has side effects"""
        logger.debug(f"Adding main subject now to {self.qid.value}")
        if match.qid is None or match.qid == "":
            raise ValueError("qid was None or empty string")
        logger.info("Adding main subject with WBI")
        # Use WikibaseIntegrator aka wbi to upload the changes in one edit
        retrieved_date = Time(
            prop_nr="P813",  # Fetched today
            time=datetime.utcnow().replace(
                tzinfo=timezone.utc
            ).replace(
                hour=0,
                minute=0,
                second=0,
            ).strftime("+%Y-%m-%dT%H:%M:%SZ")
        )
        stated_in = WbiItemType(
            prop_nr="P248",
            value=StatedIn.CROSSREF.value
        )
        stated_as = String(
            prop_nr=Property.STATED_AS.value,
            value=match.original_subject
        )
        determination_method = WbiItemType(
            prop_nr=Property.DETERMINATION_METHOD.value,
            value=DeterminationMethod.FUZZY_POWERED_NAMED_ENTITY_RECOGNITION_MATCHER.value
        )
        reference = [
            stated_in,
            stated_as,
            retrieved_date,
            determination_method,
        ]
        if reference is None:
            raise ValueError("No reference defined, cannot add usage example")
        else:
            # This is the usage example statement
            claim = WbiItemType(
                prop_nr=Property.MAIN_SUBJECT.value,
                value=match.qid.value,
                # Add qualifiers
                qualifiers=[],
                # Add reference
                references=[reference],
            )
            # if config.debug_json:
            #     logging.debug(f"claim:{claim.get_json_representation()}")
            if src.runtime_variables.login_instance is None:
                # Authenticate with WikibaseIntegrator
                with console.status("Logging in with WikibaseIntegrator..."):
                    src.runtime_variables.login_instance = wbi_login.Login(
                        user=config.bot_username,
                        password=config.password
                    )
                    # Set User-Agent
                    wbi_config.config["USER_AGENT_DEFAULT"] = config.user_agent
            wbi = WikibaseIntegrator(login=src.runtime_variables.login_instance)
            item = wbi.item.get(self.qid.value)
            item.add_claims(
                [claim],
                # This means that if the value already exist we will update it.
                action_if_exists=ActionIfExists.APPEND
            )
            # if config.debug_json:
            #     print(item.get_json_representation())
            # TODO match.label could be None, do we need to handle that?
            result = item.write(
                summary=(f"Added main subject [[{match.qid}|{match.label}]] " +
                         f"with [[Wikidata:Tools/src]] v{config.version}")
            )
            if isinstance(result, WbiEntityItem):
                console.print(f"[green]Uploaded '{match.label}' to[/green] {self.qid.history_url()}")
                match.edited_qid = self.qid
                statistics = Statistics()
                # upload_dataframe.update_forward_refs()
                statistics.match = match
                statistics.add()
            else:
                raise ValueError("Did not get an item back from WBI, something went wrong :/")
            # print("debug exit after adding to statistics")
            # exit()

    def __lookup_in_wikidata__(self):
        logger.debug("Looking up in Wikidata")
        self.__lookup_via_hub__()

    def lookup_and_match_subjects(self):
        """Looking up in CrossrefEngine, Wikidata and match subjects only if found in both"""
        self.__lookup_in_crossref__()
        self.__lookup_in_wikidata__()
        if self.crossref is not None and self.crossref.work is not None:
            logger.debug("Found in crossref_engine")
            if self.doi_found_in_wikidata:
                logger.info(f"Matching subjects for {self.wikipedia_doi} now")
                self.crossref.match_subjects()
                logger.debug(f"lookup_and_match_subjects:Found {self.crossref.work.number_of_subject_matches} matches")
                # print("debug exit after matching subjects")
                # exit()
            else:
                logger.debug("Not found in Wikidata, skipping lookup of subjects")
        else:
            logger.debug("Not found in crossref_engine")
        # if config.loglevel == logging.DEBUG:
        #     input("press enter after lookup and match")

    def upload_subjects(self):
        """Upload all the matched subjects to Wikidata"""
        if (
                self.doi_found_in_wikidata and
                self.doi_found_in_crossref
        ):
            logger.info("Found in both Wikidata and CrossrefEngine :)")
            if (
                    self.crossref.work.number_of_subject_matches > 0
            ):
                logger.info(f"Uploading {self.crossref.work.number_of_subject_matches} now to {self.qid.url()}")
                for match in self.crossref.work.subject_matches:
                    self.__upload_main_subject_using_wbi__(match=match)
            else:
                logger.info("No subject Q-items matched for this DOI")
        else:
            logger.debug("DOI not found in both Wikidata and CrossrefEngine")

    def wikidata_doi_search_url(self):
        # quote to guard against äöå and the like
        return (
                "https://www.wikidata.org/w/index.php?" +
                "search={}&title=Special%3ASearch&".format(quote(self.wikipedia_doi)) +
                "profile=advanced&fulltext=0&" +
                "advancedSearch-current=%7B%7D&ns0=1"
        )
