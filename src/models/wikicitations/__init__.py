import logging
from datetime import datetime, timezone
from time import sleep
from typing import Any, Iterable, Optional, List, Dict

from pydantic import BaseModel, validate_arguments, NoneStr
from wikibaseintegrator import wbi_config, datatypes, WikibaseIntegrator, wbi_login  # type: ignore
from wikibaseintegrator.entities import ItemEntity  # type: ignore
from wikibaseintegrator.models import Claim, Qualifiers, References, Reference  # type: ignore
from wikibaseintegrator.wbi_exceptions import NonUniqueLabelDescriptionPairError  # type: ignore
from wikibaseintegrator.wbi_exceptions import NonExistentEntityError  # type: ignore
from wikibaseintegrator.wbi_helpers import execute_sparql_query, delete_page  # type: ignore

import config
from src import console
from src.models.exceptions import MissingInformationError
from src.models.person import Person
from src.models.wikicitations.itemtypes.base_item_type import BaseItemType
from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage
from src.models.wikicitations.enums import WCDProperty, WCDItem
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

logger = logging.getLogger(__name__)


class WikiCitations(BaseModel):
    """This class models the WikiCitations Wikibase
    and handles all uploading to it

    We want to create items for all Wikipedia pages
    and references with a unique hash

    Terminology:
    page_reference is a reference that appear in a Wikipedia page
    reference_claim is a datastructure from WBI that contains the
    revision id and retrieved date of the statement

    The language code is the one used by Wikimedia Foundation"""

    language_code: str = "en"
    language_wcditem: WCDItem = WCDItem.ENGLISH_WIKIPEDIA
    reference_claim: Optional[References]

    class Config:
        arbitrary_types_allowed = True

    @validate_arguments
    def __convert_wcd_entity_id_to_item_entity__(self, entity_id: str) -> ItemEntity:
        """Convert and get the item using WBI"""
        self.__setup_wbi__()
        wbi = WikibaseIntegrator()
        return wbi.item.get(entity_id)

    # TODO refactor delete_* methods into one using a BaseItemType
    def __delete_all_page_items__(self) -> None:
        """Get all items and delete them one by one"""
        items = self.__get_all_page_items__() or []
        if number_of_items := len(items):
            logger.info(f"Got {number_of_items} bindings to delete")
            self.__setup_wbi__()
            with console.status(f"Deleting {number_of_items} page items"):
                for item_id in items:
                    logger.info(f"Deleting {item_id}")
                    self.__delete_item__(item_id=item_id)
                    # logger.debug(result)
                    if config.press_enter_to_continue:
                        input("continue?")
            console.print(f"Done deleting all {number_of_items} page items")
        else:
            console.print("Got no page items from the WCD Query Service.")

    def __delete_all_reference_items__(self) -> None:
        """Get all items and delete them one by one"""
        items = self.__get_all_reference_items__() or []
        if number_of_items := len(items):
            logger.info(f"Got {number_of_items} bindings to delete")
            self.__setup_wbi__()
            with console.status(f"Deleting {number_of_items} reference items"):
                for item_id in items:
                    logger.info(f"Deleting {item_id}")
                    self.__delete_item__(item_id=item_id)
                    # logger.debug(result)
                    if config.press_enter_to_continue:
                        input("continue?")
            console.print(f"Done deleting all {number_of_items} reference items")
        else:
            console.print("Got no reference items from the WCD Query Service.")

    def __delete_all_website_items__(self):
        """Get all items and delete them one by one"""
        items = self.__get_all_website_items__() or []
        if number_of_items := len(items):
            logger.info(f"Got {number_of_items} bindings to delete")
            self.__setup_wbi__()
            with console.status(f"Deleting {number_of_items} website items"):
                for item_id in items:
                    logger.info(f"Deleting {item_id}")
                    self.__delete_item__(item_id=item_id)
                    # logger.debug(result)
                    if config.press_enter_to_continue:
                        input("continue?")
            console.print(f"Done deleting all {number_of_items} website items")
        else:
            console.print("Got no website items from the WCD Query Service.")

    @validate_arguments
    def __delete_item__(self, item_id: str):
        if config.press_enter_to_continue:
            input(f"Do you want to delete {item_id}?")
        logger.debug(f"trying to log in with {config.user} and {config.pwd}")
        self.__setup_wbi__()
        try:
            return delete_page(
                title=f"Item:{item_id}",
                # deletetalk=True,
                login=wbi_login.Login(
                    user=config.user,
                    password=config.pwd,
                    mediawiki_api_url=config.mediawiki_api_url,
                ),
            )
        except NonExistentEntityError:
            return

    @validate_arguments
    def __extract_item_ids__(self, sparql_result: Optional[Dict]) -> Iterable[str]:
        """Yield item ids from a sparql result"""
        if sparql_result:
            yielded = 0
            for binding in sparql_result["results"]["bindings"]:
                if item_id := self.__extract_wcdqs_json_entity_id__(data=binding):
                    yielded += 1
                    yield item_id
            if number_of_bindings := len(sparql_result["results"]["bindings"]):
                logger.info(f"Yielded {yielded} bindings out of {number_of_bindings}")

    @validate_arguments
    def __extract_wcdqs_json_entity_id__(
        self, data: Dict, sparql_variable: str = "item"
    ) -> str:
        """We default to "item" as sparql value because it is customary in the Wikibase ecosystem"""
        return str(
            data[sparql_variable]["value"].replace(
                config.wikibase_rdf_entity_prefix, ""
            )
        )

    # TODO refactor these get all functions
    #  using BaseItemType and use the wcditem attribute value in the query
    @validate_arguments
    def __get_all_items__(self, item_type: BaseItemType):
        pass

    def __get_all_page_items__(self):
        """Get all wcdqids for wikipedia pages using sparql"""
        return self.__extract_item_ids__(
            sparql_result=self.__get_items_via_sparql__(
                """
            prefix wcd: <http://wikicitations.wiki.opencura.com/entity/>
            prefix wcdt: <http://wikicitations.wiki.opencura.com/prop/direct/>
            SELECT ?item WHERE {
              ?item wcdt:P10 wcd:Q6
            }
            """
            )
        )

    def __get_all_reference_items__(self):
        """Get all wcdqids for references using sparql"""
        return self.__extract_item_ids__(
            sparql_result=self.__get_items_via_sparql__(
                """
            prefix wcd: <http://wikicitations.wiki.opencura.com/entity/>
            prefix wcdt: <http://wikicitations.wiki.opencura.com/prop/direct/>
            SELECT ?item WHERE {
                ?item wcdt:P10 wcd:Q4
            }
            """
            )
        )

    def __get_all_website_items__(self):
        """Get all wcdqids for website items using sparql"""
        return self.__extract_item_ids__(
            sparql_result=self.__get_items_via_sparql__(
                """
            prefix wcd: <http://wikicitations.wiki.opencura.com/entity/>
            prefix wcdt: <http://wikicitations.wiki.opencura.com/prop/direct/>
            SELECT ?item WHERE {
                ?item wcdt:P10 wcd:Q145
            }
            """
            )
        )

    @validate_arguments
    def __get_item_entity_from_wcdqs_json__(
        self, data: Dict, sparql_variable: str = "item"
    ) -> ItemEntity:
        return self.__convert_wcd_entity_id_to_item_entity__(
            self.__extract_wcdqs_json_entity_id__(
                data=data, sparql_variable=sparql_variable
            )
        )

    @validate_arguments
    def __get_items_via_sparql__(self, query: str) -> Any:
        """This is the lowest level function
        that executes the query with WBI after setting it up"""
        self.__setup_wbi__()
        self.__wait_for_wcdqs_to_sync__()
        return execute_sparql_query(query=query, endpoint=config.sparql_endpoint_url)

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __get_wcdqid_from_error_message__(
        self, mw_api_error: NonUniqueLabelDescriptionPairError
    ) -> str:
        """This method extracts the WCDQID from the Wikibase error message."""
        expected_error_name = "wikibase-validator-label-with-description-conflict"
        error_message = mw_api_error.error_msg
        if "error" in error_message:
            error_dict = error_message["error"]
            if "messages" in error_dict:
                # This is an array
                messages = error_dict["messages"]
                first_message = messages[0]
                if "name" in first_message:
                    name = first_message["name"]
                    if name == expected_error_name:
                        if "parameters" in first_message:
                            # This is a list e.g.:
                            """'parameters': [
                              'google.com',
                              'en',
                              '[[Item:Q562|Q562]]'
                            ],"""
                            parameters = first_message["parameters"]
                            wcdqid_wikitext = parameters[2].split("|")
                            # We cut away the last to chars "]]"
                            wcdqid = wcdqid_wikitext[1][:-2]
                            return str(wcdqid)
                        else:
                            raise ValueError("no parameters in first_message")
                    else:
                        raise ValueError(
                            f"Name was '{name}' but we expected '{expected_error_name}' "
                            f"in the first message of the the error response text from Wikibase."
                        )
                else:
                    raise MissingInformationError(
                        "No name in the first message in the error response text from Wikibase."
                    )
            else:
                raise MissingInformationError(
                    "No messages in the error response text from Wikibase."
                )
        else:
            raise MissingInformationError(
                "No error dict in the error response text from Wikibase."
            )

    @validate_arguments
    def __get_wcdqids_from_hash__(self, md5hash: str) -> List[str]:
        """This is a slower SPARQL-powered fallback helper method
        used when config.use_cache is False"""
        logger.debug("__get_wcdqid_from_hash__: running")
        query = f"""
            prefix wcdt: <http://wikicitations.wiki.opencura.com/prop/direct/>
            SELECT ?item WHERE {{
              ?item wcdt:P30 "{md5hash}".
            }}
        """
        return list(
            self.__extract_item_ids__(
                sparql_result=self.__get_items_via_sparql__(query=query)
            )
        )

    @validate_arguments
    def __prepare_all_person_claims__(
        self, page_reference: WikipediaPageReference
    ) -> List[Claim]:
        authors = self.__prepare_person_claims__(
            use_list=page_reference.authors_list,
            property=WCDProperty.FULL_NAME_STRING,
        )
        if (
            config.assume_persons_without_role_are_authors
            and page_reference.persons_without_role
        ):
            logger.info("Assuming persons without role are authors")
        no_role_authors = self.__prepare_person_claims__(
            use_list=page_reference.persons_without_role,
            property=WCDProperty.FULL_NAME_STRING,
        )
        editors = self.__prepare_person_claims__(
            use_list=page_reference.interviewers_list,
            property=WCDProperty.EDITOR_NAME_STRING,
        )
        hosts = self.__prepare_person_claims__(
            use_list=page_reference.hosts_list,
            property=WCDProperty.HOST_STRING,
        )
        interviewers = self.__prepare_person_claims__(
            use_list=page_reference.interviewers_list,
            property=WCDProperty.INTERVIEWER_STRING,
        )
        translators = self.__prepare_person_claims__(
            use_list=page_reference.interviewers_list,
            property=WCDProperty.INTERVIEWER_STRING,
        )
        return authors + no_role_authors + editors + hosts + interviewers + translators

    @validate_arguments
    def __prepare_item_citations__(self, wikipedia_page: WikipediaPage) -> List[Claim]:
        """Prepare the item citations and add a reference
        to in which revision it was found and the retrieval date"""
        logger.info("Preparing item citations")
        claims = []
        for reference in wikipedia_page.references or []:
            if reference.wikicitations_qid:
                logger.debug("Appending to citations")
                claims.append(
                    datatypes.Item(
                        prop_nr=WCDProperty.CITATIONS.value,
                        value=reference.wikicitations_qid,
                        references=self.reference_claim,
                    )
                )
        return claims

    @validate_arguments
    def __prepare_new_reference_item__(
        self, page_reference: WikipediaPageReference, wikipedia_page: WikipediaPage
    ) -> ItemEntity:
        """This method converts a page_reference into a new reference item"""
        self.__setup_wbi__()
        wbi = WikibaseIntegrator(
            login=wbi_login.Login(user=config.user, password=config.pwd),
        )
        item = wbi.item.new()
        # We append the first 7 chars of the hash to the title
        # to avoid label collision errors
        assert page_reference.md5hash, "Assure mypy that it is not None"
        item.labels.set("en", f"{page_reference.title} | {page_reference.md5hash[:7]}")
        item.descriptions.set(
            "en", f"reference from {wikipedia_page.wikimedia_site.name.title()}"
        )
        persons = self.__prepare_all_person_claims__(page_reference=page_reference)
        if persons:
            item.add_claims(persons)
        item.add_claims(
            self.__prepare_single_value_reference_claims__(
                page_reference=page_reference
            ),
        )
        # if config.loglevel == logging.DEBUG:
        #     logger.debug("Printing the item data")
        #     print(item.get_json())
        #     # exit()
        return item

    def __prepare_new_website_item__(
        self, page_reference: WikipediaPageReference, wikipedia_page: WikipediaPage
    ) -> ItemEntity:
        """This method converts a page_reference into a new website item"""
        if page_reference.first_level_domain_of_url is None:
            raise MissingInformationError(
                "page_reference.first_level_domain_of_url was None"
            )
        logger.info(
            f"Creating website item: {page_reference.first_level_domain_of_url}"
        )
        self.__setup_wbi__()
        wbi = WikibaseIntegrator(
            login=wbi_login.Login(user=config.user, password=config.pwd),
        )
        item = wbi.item.new()
        item.labels.set("en", page_reference.first_level_domain_of_url)
        item.descriptions.set(
            "en",
            f"website referenced from {wikipedia_page.wikimedia_site.name.title()}",
        )
        item.add_claims(
            self.__prepare_single_value_website_claims__(page_reference=page_reference),
        )
        # if config.loglevel == logging.DEBUG:
        #     logger.debug("Printing the item data")
        #     print(item.get_json())
        #     # exit()
        return item

    @validate_arguments
    def __prepare_new_wikipedia_page_item__(
        self, wikipedia_page: WikipediaPage
    ) -> ItemEntity:
        """This method converts a page_reference into a new WikiCitations item"""
        logging.debug("__prepare_new_wikipedia_page_item__: Running")
        self.__setup_wbi__()
        wbi = WikibaseIntegrator(
            login=wbi_login.Login(user=config.user, password=config.pwd),
        )
        item = wbi.item.new()
        item.labels.set("en", wikipedia_page.title)
        item.descriptions.set(
            "en",
            f"page from {wikipedia_page.language_code}:{wikipedia_page.wikimedia_site.name.title()}",
        )
        # Prepare claims
        # First prepare the page_reference needed in other claims
        citations = self.__prepare_item_citations__(wikipedia_page=wikipedia_page)
        string_citations = self.__prepare_string_citations__(
            wikipedia_page=wikipedia_page
        )
        if citations:
            item.add_claims(citations)
        if string_citations:
            item.add_claims(string_citations)
        item.add_claims(
            self.__prepare_single_value_wikipedia_page_claims__(
                wikipedia_page=wikipedia_page
            ),
        )
        if config.loglevel == logging.DEBUG:
            logger.debug("Printing the item data")
            print(item.get_json())
            # exit()
        return item

    @validate_arguments
    def __prepare_person_claims__(
        self,
        use_list: Optional[List[Person]],
        property: WCDProperty,
    ) -> List:
        """Prepare claims using the specified property and list of person objects"""
        persons = []
        use_list = use_list or []
        if use_list:
            logger.debug(f"Preparing {property.name}")
            for person_object in use_list:
                # We use this pythonic way of checking if the string is empty inspired by:
                # https://www.delftstack.com/howto/python/how-to-check-a-string-is-empty-in-a-pythonic-way/
                if person_object.full_name:
                    qualifiers = (
                        self.__prepare_person_qualifiers__(person_object=person_object)
                        or []
                    )
                    if qualifiers:
                        person = datatypes.String(
                            prop_nr=property.value,
                            value=person_object.full_name,
                            qualifiers=qualifiers,
                        )
                    else:
                        person = datatypes.String(
                            prop_nr=property.value,
                            value=person_object.full_name,
                        )
                    persons.append(person)
        return persons

    @validate_arguments
    def __prepare_person_qualifiers__(self, person_object: Person):
        qualifiers = []
        if (
            person_object.given
            or person_object.given
            or person_object.orcid
            or person_object.number_in_sequence
        ):
            if person_object.given:
                given_name = datatypes.String(
                    prop_nr=WCDProperty.GIVEN_NAME.value,
                    value=person_object.given,
                )
                qualifiers.append(given_name)
            if person_object.surname:
                surname = datatypes.String(
                    prop_nr=WCDProperty.FAMILY_NAME.value,
                    value=person_object.surname,
                )
                qualifiers.append(surname)
            if person_object.number_in_sequence:
                number_in_sequence = datatypes.Quantity(
                    prop_nr=WCDProperty.SERIES_ORDINAL.value,
                    amount=person_object.number_in_sequence,
                )
                qualifiers.append(number_in_sequence)
            if person_object.orcid:
                orcid = datatypes.ExternalID(
                    prop_nr=WCDProperty.ORCID.value,
                    value=person_object.orcid,
                )
                qualifiers.append(orcid)
            if person_object.link:
                link = datatypes.URL(
                    prop_nr=WCDProperty.URL.value,
                    value=person_object.link,
                )
                qualifiers.append(link)
            if person_object.mask:
                mask = datatypes.String(
                    prop_nr=WCDProperty.NAME_MASK.value,
                    value=person_object.mask,
                )
                qualifiers.append(mask)
        return qualifiers

    @validate_arguments
    def __prepare_reference_claim__(self, wikipedia_page: WikipediaPage):
        """This reference claim contains the current revision id and the current date
        This enables us to track references over time in the graph using SPARQL."""
        logger.info("Preparing reference claim")
        # Prepare page_reference
        retrieved_date = datatypes.Time(
            prop_nr=WCDProperty.RETRIEVED_DATE.value,
            time=datetime.utcnow()  # Fetched today
            .replace(tzinfo=timezone.utc)
            .replace(
                hour=0,
                minute=0,
                second=0,
            )
            .strftime("+%Y-%m-%dT%H:%M:%SZ"),
        )
        revision_id = datatypes.String(
            prop_nr=WCDProperty.PAGE_REVISION_ID.value,
            value=str(wikipedia_page.latest_revision_id),
        )
        claims = [retrieved_date, revision_id]
        citation_reference = Reference()
        for claim in claims:
            logger.debug(f"Adding reference {claim}")
            citation_reference.add(claim)
        self.reference_claim = References()
        self.reference_claim.add(citation_reference)

    def __prepare_single_value_reference_claims__(
        self,
        page_reference: WikipediaPageReference,
    ) -> Optional[List[Claim]]:
        logger.info("Preparing single value claims")
        # Claims always present
        instance_of = datatypes.Item(
            prop_nr=WCDProperty.INSTANCE_OF.value,
            value=WCDItem.WIKIPEDIA_REFERENCE.value,
        )
        if page_reference.template_name:
            website_string = datatypes.String(
                prop_nr=WCDProperty.TEMPLATE_NAME.value,
                value=page_reference.template_name,
            )
        else:
            raise ValueError("no template name found")
        retrieved_date = datatypes.Time(
            prop_nr=WCDProperty.RETRIEVED_DATE.value,
            time=datetime.utcnow()  # Fetched today
            .replace(tzinfo=timezone.utc)
            .replace(
                hour=0,
                minute=0,
                second=0,
            )
            .strftime("+%Y-%m-%dT%H:%M:%SZ"),
        )
        source_wikipedia = datatypes.Item(
            prop_nr=WCDProperty.SOURCE_WIKIPEDIA.value,
            value=self.language_wcditem.value,
        )
        if page_reference.md5hash is None:
            raise ValueError("page_reference.md5hash was None")
        hash_claim = datatypes.String(
            prop_nr=WCDProperty.HASH.value, value=page_reference.md5hash
        )
        # Optional claims
        # TODO unify and refactor if possible
        access_date = None
        doi = None
        isbn_10 = None
        isbn_13 = None
        lumped_authors = None
        orcid = None
        pmid = None
        publication_date = None
        template_name = None
        title = None
        url = None
        wikidata_qid = None
        if page_reference.access_date:
            access_date = datatypes.Time(
                prop_nr=WCDProperty.ACCESS_DATE.value,
                time=(
                    page_reference.access_date.replace(tzinfo=timezone.utc)
                    .replace(
                        hour=0,
                        minute=0,
                        second=0,
                    )
                    .strftime("+%Y-%m-%dT%H:%M:%SZ")
                ),
            )
        if page_reference.doi:
            doi = datatypes.ExternalID(
                prop_nr=WCDProperty.DOI.value,
                value=page_reference.doi,
            )
        if page_reference.isbn_10:
            isbn_10 = datatypes.ExternalID(
                prop_nr=WCDProperty.ISBN_10.value,
                value=page_reference.isbn_10,
            )
        if page_reference.isbn_13:
            isbn_13 = datatypes.ExternalID(
                prop_nr=WCDProperty.ISBN_13.value,
                value=page_reference.isbn_13,
            )
        if page_reference.location:
            location = datatypes.String(
                prop_nr=WCDProperty.LOCATION_STRING.value, value=page_reference.location
            )
        else:
            location = None
        if page_reference.vauthors:
            lumped_authors = datatypes.String(
                prop_nr=WCDProperty.LUMPED_AUTHORS.value,
                value=page_reference.vauthors,
            )
        if page_reference.orcid:
            orcid = datatypes.ExternalID(
                prop_nr=WCDProperty.ORCID.value,
                value=page_reference.orcid,
            )
        if page_reference.pmid:
            pmid = datatypes.ExternalID(
                prop_nr=WCDProperty.PMID.value,
                value=page_reference.pmid,
            )
        if page_reference.publication_date:
            publication_date = datatypes.Time(
                prop_nr=WCDProperty.PUBLICATION_DATE.value,
                time=(
                    page_reference.publication_date.replace(tzinfo=timezone.utc)
                    .replace(
                        hour=0,
                        minute=0,
                        second=0,
                    )
                    .strftime("+%Y-%m-%dT%H:%M:%SZ")
                ),
            )
        if page_reference.publisher:
            publisher = datatypes.String(
                prop_nr=WCDProperty.PUBLISHER_STRING.value,
                value=page_reference.publisher,
            )
        else:
            publisher = None
        if page_reference.title:
            title = datatypes.MonolingualText(
                prop_nr=WCDProperty.TITLE.value,
                text=page_reference.title,
                language=self.language_code,
            )
        if page_reference.url:
            url = datatypes.URL(
                prop_nr=WCDProperty.URL.value,
                value=page_reference.url,
            )
        if page_reference.website:
            website_string = datatypes.String(
                prop_nr=WCDProperty.WEBSITE_STRING.value,
                value=page_reference.website,
            )
        # Website item
        if page_reference.first_level_domain_of_url_qid:
            website_item = datatypes.Item(
                prop_nr=WCDProperty.WEBSITE.value,
                value=page_reference.first_level_domain_of_url_qid,
            )
        else:
            website_item = None
        if page_reference.wikidata_qid:
            wikidata_qid = datatypes.ExternalID(
                prop_nr=WCDProperty.PMID.value,
                value=page_reference.wikidata_qid,
            )
        claims = []
        for claim in (
            access_date,
            doi,
            hash_claim,
            instance_of,
            isbn_10,
            isbn_13,
            location,
            lumped_authors,
            orcid,
            pmid,
            publication_date,
            publisher,
            retrieved_date,
            source_wikipedia,
            template_name,
            title,
            url,
            website_string,
            website_item,
            wikidata_qid,
        ):
            if claim:
                claims.append(claim)
        return claims

    def __prepare_single_value_website_claims__(
        self,
        page_reference: WikipediaPageReference,
    ) -> Optional[List[Claim]]:
        logger.info("Preparing single value claims for the website item")
        # Claims always present
        instance_of = datatypes.Item(
            prop_nr=WCDProperty.INSTANCE_OF.value,
            value=WCDItem.WEBSITE.value,
        )
        source_wikipedia = datatypes.Item(
            prop_nr=WCDProperty.SOURCE_WIKIPEDIA.value,
            value=self.language_wcditem.value,
        )
        first_level_domain_string = datatypes.String(
            prop_nr=WCDProperty.FIRST_LEVEL_DOMAIN_STRING.value,
            value=page_reference.first_level_domain_of_url,
        )
        if page_reference.first_level_domain_of_url_hash is None:
            raise ValueError("page_reference.first_level_domain_of_url_hash was None")
        hash_claim = datatypes.String(
            prop_nr=WCDProperty.HASH.value,
            value=page_reference.first_level_domain_of_url_hash,
        )
        return [
            claim
            for claim in (
                instance_of,
                source_wikipedia,
                first_level_domain_string,
                hash_claim,
            )
            if claim
        ]

    def __prepare_single_value_wikipedia_page_claims__(
        self, wikipedia_page
    ) -> List[Claim]:
        # There are no optional claims for Wikipedia Pages
        absolute_url = datatypes.URL(
            prop_nr=WCDProperty.URL.value,
            value=wikipedia_page.absolute_url,
        )
        if wikipedia_page.md5hash is None:
            raise ValueError("wikipedia_page.md5hash was None")
        hash_claim = datatypes.String(
            prop_nr=WCDProperty.HASH.value, value=wikipedia_page.md5hash
        )
        instance_of = datatypes.Item(
            prop_nr=WCDProperty.INSTANCE_OF.value,
            value=WCDItem.WIKIPEDIA_PAGE.value,
        )
        last_update = datatypes.Time(
            prop_nr=WCDProperty.LAST_UPDATE.value,
            time=datetime.utcnow()  # Fetched today
            .replace(tzinfo=timezone.utc)
            .replace(
                hour=0,
                minute=0,
                second=0,
            )
            .strftime("+%Y-%m-%dT%H:%M:%SZ"),
        )
        if wikipedia_page.page_id is None:
            raise ValueError("wikipedia_page.page_id was None")
        page_id = datatypes.String(
            prop_nr=WCDProperty.MEDIAWIKI_PAGE_ID.value,
            value=str(wikipedia_page.page_id),
        )
        published_in = datatypes.Item(
            prop_nr=WCDProperty.PUBLISHED_IN.value,
            value=self.language_wcditem.value,
        )
        if wikipedia_page.title is None:
            raise ValueError("wikipedia_page.item_id was None")
        title = datatypes.MonolingualText(
            prop_nr=WCDProperty.TITLE.value,
            text=wikipedia_page.title,
            language=self.language_code,
        )
        return [
            absolute_url,
            hash_claim,
            instance_of,
            last_update,
            page_id,
            published_in,
            title,
        ]

    @staticmethod
    def __prepare_string_authors__(page_reference: WikipediaPageReference):
        authors = []
        for author in page_reference.authors_list or []:
            if author.full_name:
                author = datatypes.String(
                    prop_nr=WCDProperty.FULL_NAME_STRING.value,
                    value=author.full_name,
                )
                authors.append(author)
        if page_reference.vauthors:
            author = datatypes.String(
                prop_nr=WCDProperty.LUMPED_AUTHORS.value,
                value=page_reference.vauthors,
            )
            authors.append(author)
        if page_reference.authors:
            author = datatypes.String(
                prop_nr=WCDProperty.LUMPED_AUTHORS.value,
                value=page_reference.authors,
            )
            authors.append(author)
        return authors or None

    @staticmethod
    def __prepare_string_editors__(page_reference: WikipediaPageReference):
        persons = []
        for person in page_reference.editors_list or []:
            if person.full_name:
                person = datatypes.String(
                    prop_nr=WCDProperty.EDITOR_NAME_STRING.value,
                    value=person.full_name,
                )
                persons.append(person)
        return persons or None

    @staticmethod
    def __prepare_string_translators__(page_reference: WikipediaPageReference):
        persons = []
        for person in page_reference.translators_list or []:
            if person.full_name:
                person = datatypes.String(
                    prop_nr=WCDProperty.TRANSLATOR_NAME_STRING.value,
                    value=person.full_name,
                )
                persons.append(person)
        return persons or None

    @validate_arguments()
    def __prepare_string_citation__(
        self, page_reference: WikipediaPageReference
    ) -> Claim:
        """We import citations which could not be uniquely identified
        as strings directly on the wikipedia page item"""
        qualifiers = self.__prepare_string_citation_qualifiers__(
            page_reference=page_reference
        )
        claim_qualifiers = Qualifiers()
        for qualifier in qualifiers:
            logger.debug(f"Adding qualifier {qualifier}")
            claim_qualifiers.add(qualifier)
        string_citation = datatypes.String(
            prop_nr=WCDProperty.STRING_CITATIONS.value,
            value=page_reference.template_name,
            qualifiers=claim_qualifiers,
            references=self.reference_claim,
        )
        return string_citation

    def __prepare_string_citation_qualifiers__(
        self, page_reference: WikipediaPageReference
    ) -> List[Claim]:
        """Here we prepare all statements we normally
        would put on a unique separate page_reference item"""
        claims = []
        string_authors = self.__prepare_string_authors__(page_reference=page_reference)
        if string_authors:
            claims.extend(string_authors)
        string_editors = self.__prepare_string_editors__(page_reference=page_reference)
        if string_editors:
            claims.extend(string_editors)
        string_translators = self.__prepare_string_translators__(
            page_reference=page_reference
        )
        if string_translators:
            claims.extend(string_translators)
        access_date = None
        archive_date = None
        archive_url = None
        publication_date = None
        title = None
        url = None
        website_string = None
        if page_reference.access_date:
            access_date = datatypes.Time(
                prop_nr=WCDProperty.ACCESS_DATE.value,
                time=(
                    page_reference.access_date.replace(tzinfo=timezone.utc)
                    .replace(
                        hour=0,
                        minute=0,
                        second=0,
                    )
                    .strftime("+%Y-%m-%dT%H:%M:%SZ")
                ),
            )
        if page_reference.archive_date:
            access_date = datatypes.Time(
                prop_nr=WCDProperty.ARCHIVE_DATE.value,
                time=(
                    page_reference.archive_date.replace(tzinfo=timezone.utc)
                    .replace(
                        hour=0,
                        minute=0,
                        second=0,
                    )
                    .strftime("+%Y-%m-%dT%H:%M:%SZ")
                ),
            )
        if page_reference.archive_url:
            archive_url = datatypes.URL(
                prop_nr=WCDProperty.ARCHIVE_URL.value,
                value=page_reference.archive_url,
            )
        if page_reference.publication_date:
            publication_date = datatypes.Time(
                prop_nr=WCDProperty.PUBLICATION_DATE.value,
                time=(
                    page_reference.publication_date.replace(tzinfo=timezone.utc)
                    .replace(
                        hour=0,
                        minute=0,
                        second=0,
                    )
                    .strftime("+%Y-%m-%dT%H:%M:%SZ")
                ),
            )
        if page_reference.title:
            title = datatypes.MonolingualText(
                prop_nr=WCDProperty.TITLE.value,
                text=page_reference.title,
                language=self.language_code,
            )
        if page_reference.url:
            url = datatypes.URL(
                prop_nr=WCDProperty.URL.value,
                value=page_reference.url,
            )
        if page_reference.website:
            website_string = datatypes.String(
                prop_nr=WCDProperty.WEBSITE_STRING.value,
                value=page_reference.website,
            )
        for claim in (
            access_date,
            archive_date,
            archive_url,
            publication_date,
            title,
            url,
            website_string,
        ):
            if claim:
                claims.append(claim)
        return claims

    def __prepare_string_citations__(
        self, wikipedia_page: WikipediaPage
    ) -> List[Claim]:
        # pseudo code
        # Return a citation for every page_reference that does not have a hash
        return [
            self.__prepare_string_citation__(page_reference=page_reference)
            for page_reference in (wikipedia_page.references or [])
            if not page_reference.has_hash
        ]

    @staticmethod
    def __setup_wbi__() -> None:
        wbi_config.config["USER_AGENT"] = "wcdimportbot"
        wbi_config.config["WIKIBASE_URL"] = config.wikibase_url
        wbi_config.config["MEDIAWIKI_API_URL"] = config.mediawiki_api_url
        wbi_config.config["MEDIAWIKI_INDEX_URL"] = config.mediawiki_index_url
        wbi_config.config["SPARQL_ENDPOINT_URL"] = config.sparql_endpoint_url
        return None

    def __upload_new_item__(self, item: ItemEntity) -> str:
        """Upload the new item to WikiCitations"""
        if item is None:
            raise ValueError("Did not get what we need")
        if config.loglevel == logging.DEBUG:
            logger.debug("Finished item JSON")
            console.print(item.get_json())
            # exit()
        try:
            new_item = item.write(summary="New item imported from Wikipedia")
            print(f"Added new item {self.entity_url(new_item.id)}")
            if config.press_enter_to_continue:
                input("press enter to continue")
            logger.debug(f"returning new wcdqid: {new_item.id}")
            return str(new_item.id)
        except NonUniqueLabelDescriptionPairError as e:
            """Catch and extract the WCDQID
            Example response:
            {
              'error': {
                'code': 'modification-failed',
                'info': 'Item [[Item:Q562|Q562]] already has label "google.com" associated with language code en, using the same description text.',
                'messages': [
                  {
                    'name': 'wikibase-validator-label-with-description-conflict',
                    'parameters': [
                      'google.com',
                      'en',
                      '[[Item:Q562|Q562]]'
                    ],
                    'html': {
                      '*': 'Item <a href="/wiki/Item:Q562" title="Item:Q562">Q562</a> already has label "google.com" associated with language code en, using the same description text.'
                    }
                  }
                ],
                '*': 'See   tps://wikicitations.wiki.opencura.com/w/api.php for API usage. Subscribe to the mediawiki-api-announce mailing list at &lt;https://lists.wikimedia.org/mailman/listinfo/mediawiki-api-announce&gt; for notice of API deprecations and breaking changes.'
              }
            }"""
            logger.info(e)
            wcdqid = self.__get_wcdqid_from_error_message__(mw_api_error=e)
            return wcdqid

    @staticmethod
    def __wait_for_wcdqs_to_sync__():
        logger.info(
            f"Sleeping {config.sparql_sync_waiting_time_in_seconds} seconds for WCDQS to sync"
        )
        sleep(config.sparql_sync_waiting_time_in_seconds)

    def delete_imported_items(self):
        """This function deletes all the imported items in WikiCitations"""
        console.print("Deleting all imported items")
        self.__delete_all_page_items__()
        self.__delete_all_reference_items__()
        self.__delete_all_website_items__()

    @staticmethod
    @validate_arguments
    def entity_url(qid: str):
        return f"{config.wikibase_url}/wiki/Item:{qid}"

    @validate_arguments
    def get_item(self, item_id: str) -> Optional[ItemEntity]:
        """Get one item from WikiCitations"""
        self.__setup_wbi__()
        wbi = WikibaseIntegrator()
        return wbi.item.get(item_id)

    @validate_arguments
    def prepare_and_upload_reference_item(
        self, page_reference: WikipediaPageReference, wikipedia_page: WikipediaPage
    ) -> str:
        """This method prepares and then tries to upload the reference to WikiCitations
        and returns the WCDQID either if successfull upload or from the
        Wikibase error if an item with the exact same label/hash already exists.

        A possible speedup would be to only prepare the label and description
        and try to upload. If successfull add all the statements to the item.
        This saves us from computing all the statements and discard them on error"""
        self.__prepare_reference_claim__(wikipedia_page=wikipedia_page)
        item = self.__prepare_new_reference_item__(
            page_reference=page_reference, wikipedia_page=wikipedia_page
        )
        wcdqid = self.__upload_new_item__(item=item)
        return wcdqid

    @validate_arguments
    def prepare_and_upload_website_item(
        self,
        page_reference: WikipediaPageReference,
        wikipedia_page: WikipediaPage,
    ) -> str:
        self.__prepare_reference_claim__(wikipedia_page=wikipedia_page)
        item = self.__prepare_new_website_item__(
            page_reference=page_reference, wikipedia_page=wikipedia_page
        )
        wcdqid = self.__upload_new_item__(item=item)
        return wcdqid

    @validate_arguments
    def prepare_and_upload_wikipedia_page_item(self, wikipedia_page: Any) -> NoneStr:
        logging.debug("prepare_and_upload_wikipedia_page_item: Running")
        from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

        if not isinstance(wikipedia_page, WikipediaPage):
            raise ValueError("did not get a WikipediaPage object")
        self.__prepare_reference_claim__(wikipedia_page=wikipedia_page)
        item = self.__prepare_new_wikipedia_page_item__(wikipedia_page=wikipedia_page)
        wcdqid = self.__upload_new_item__(item=item)
        return wcdqid
