import logging
from datetime import datetime, timezone
from typing import Any, Optional, List, Dict

from pydantic import BaseModel, validate_arguments
from wikibaseintegrator import wbi_config, datatypes, WikibaseIntegrator, wbi_login
from wikibaseintegrator.entities import ItemEntity
from wikibaseintegrator.models import Claim, Qualifiers, References, Reference
from wikibaseintegrator.wbi_helpers import execute_sparql_query, delete_page

import config
from src import console
from src.models.person import Person
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
        self.__setup_wbi__()
        wbi = WikibaseIntegrator()
        return wbi.item.get(entity_id)

    def __delete_all_page_items__(self):
        """Get all items and delete them one by one"""
        items = self.__extract_item_ids__(sparql_result=self.__get_all_page_items__())
        if items is not None and len(items) > 0:
            number_of_items = len(items)
            logger.info(f"Got {number_of_items} bindings to delete")
            self.__setup_wbi__()
            with console.status(f"Deleting {number_of_items} page items"):
                for item_id in items:
                    logger.info(f"Deleting {item_id}")
                    result = self.__delete_item__(item_id=item_id)
                    # logger.debug(result)
                    if config.press_enter_to_continue:
                        input("continue?")
            console.print(f"Done deleting all {number_of_items} page items")
        else:
            console.print("Got no page items from the WCD Query Service.")

    def __delete_all_reference_items__(self):
        """Get all items and delete them one by one"""
        items = self.__extract_item_ids__(
            sparql_result=self.__get_all_reference_items__()
        )
        if items is not None and len(items) > 0:
            number_of_items = len(items)
            logger.info(f"Got {number_of_items} bindings to delete")
            self.__setup_wbi__()
            with console.status(f"Deleting {number_of_items} reference items"):
                for item_id in items:
                    logger.info(f"Deleting {item_id}")
                    result = self.__delete_item__(item_id=item_id)
                    # logger.debug(result)
                    if config.press_enter_to_continue:
                        input("continue?")
            console.print(f"Done deleting all {number_of_items} reference items")
        else:
            console.print("Got no reference items from the WCD Query Service.")

    @validate_arguments
    def __delete_item__(self, item_id: str):
        if config.press_enter_to_continue:
            input(f"Do you want to delete {item_id}?")

        return delete_page(
            title=f"Item:{item_id}",
            # deletetalk=True,
            login=wbi_login.Login(user=config.user, password=config.pwd),
        )

    @validate_arguments
    def __extract_item_ids__(self, sparql_result: Optional[Dict]):
        """Extract item ids from the sparql result"""
        if sparql_result is not None:
            bindings = sparql_result["results"]["bindings"]
            number_of_bindings = len(bindings)
            if number_of_bindings > 0:
                items = []
                logger.info(f"Got {number_of_bindings} bindings")
                for binding in bindings:
                    item_id = self.__extract_wcdqs_json_entity_id__(data=binding)
                    if item_id is not None:
                        items.append(item_id)
                return items

    @validate_arguments
    def __extract_wcdqs_json_entity_id__(
        self, data: Dict, sparql_variable: str = "item"
    ) -> str:
        """We default to "item" as sparql value because it is customary in the Wikibase ecosystem"""
        return data[sparql_variable]["value"].replace(
            config.wikibase_rdf_entity_prefix, ""
        )

    def __get_all_page_items__(self):
        """Get all wcdqids for wikipedia pages using sparql"""
        return self.__get_items_via_sparql__(
            """
            prefix wcd: <http://wikicitations.wiki.opencura.com/entity/>
            prefix wcdt: <http://wikicitations.wiki.opencura.com/prop/direct/>
            SELECT ?item WHERE {
              ?item wcdt:P10 wcd:Q6
            }
            """
        )

    def __get_all_reference_items__(self):
        """Get all wcdqids for wikipedia pages using sparql"""
        return self.__get_items_via_sparql__(
            """
            prefix wcd: <http://wikicitations.wiki.opencura.com/entity/>
            prefix wcdt: <http://wikicitations.wiki.opencura.com/prop/direct/>
            SELECT ?item WHERE {
                ?item wcdt:P10 wcd:Q4
            }
            """
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
    def __get_items_via_sparql__(self, query: str) -> Optional[Dict[str, Dict]]:
        self.__setup_wbi__()
        return execute_sparql_query(query=query, endpoint=config.sparql_endpoint_url)

    @validate_arguments
    def __prepare_person_claims__(
        self,
        use_list: List[Person],
        property: WCDProperty,
    ):
        """Prepare claims using the specified property and list of person objects"""
        persons = []
        if use_list is not None and len(use_list) > 0:
            logger.debug(f"Preparing {property.name}")
            for person_object in use_list:
                if person_object.author_name_string is not None:
                    qualifiers = self.__prepare_person_qualifiers__(
                        person_object=person_object
                    )
                    if len(qualifiers) > 0:
                        person = datatypes.String(
                            prop_nr=property.value,
                            value=person_object.author_name_string,
                            qualifiers=qualifiers,
                        )
                    else:
                        person = datatypes.String(
                            prop_nr=property.value,
                            value=person_object.author_name_string,
                        )
                    persons.append(person)
        return persons

    @validate_arguments
    def __prepare_all_person_claims__(
        self, page_reference: WikipediaPageReference
    ) -> List[Claim]:
        persons = []
        authors = self.__prepare_person_claims__(
            use_list=page_reference.authors_list,
            property=WCDProperty.AUTHOR_NAME_STRING,
        )
        if authors is not None:
            persons.extend(authors)
        if (
            config.assume_persons_without_role_are_authors
            and page_reference.persons_without_role is not None
            and len(page_reference.persons_without_role) > 0
        ):
            logger.info("Assuming persons without role are authors")
        no_role_authors = self.__prepare_person_claims__(
            use_list=page_reference.persons_without_role,
            property=WCDProperty.AUTHOR_NAME_STRING,
        )
        if no_role_authors is not None:
            persons.extend(no_role_authors)
        editors = self.__prepare_person_claims__(
            use_list=page_reference.interviewers_list,
            property=WCDProperty.EDITOR_NAME_STRING,
        )
        if editors is not None:
            persons.extend(editors)
        hosts = self.__prepare_person_claims__(
            use_list=page_reference.hosts_list,
            property=WCDProperty.HOST_STRING,
        )
        if hosts is not None:
            persons.extend(hosts)
        interviewers = self.__prepare_person_claims__(
            use_list=page_reference.interviewers_list,
            property=WCDProperty.INTERVIEWER_STRING,
        )
        if interviewers is not None:
            persons.extend(interviewers)
        translators = self.__prepare_person_claims__(
            use_list=page_reference.interviewers_list,
            property=WCDProperty.INTERVIEWER_STRING,
        )
        if translators is not None:
            persons.extend(translators)
        return persons

    @validate_arguments
    def __prepare_item_citations__(
        self, wikipedia_page: WikipediaPage
    ) -> Optional[List[Claim]]:
        """Prepare the item citations and add a reference
        to in which revision it was found and the retrieval date"""
        logger.info("Preparing item citations")
        claims = []
        for reference in wikipedia_page.references:
            if reference.wikicitations_qid is not None:
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
        """This method converts a page_reference into a new WikiCitations item"""
        self.__setup_wbi__()
        wbi = WikibaseIntegrator(
            login=wbi_login.Login(user=config.user, password=config.pwd),
        )
        item = wbi.item.new()
        item.labels.set("en", page_reference.title)
        item.descriptions.set(
            "en", f"reference from {wikipedia_page.wikimedia_site.name.title()}"
        )
        persons = self.__prepare_all_person_claims__(page_reference=page_reference)
        if len(persons) > 0:
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
        if citations is not None and len(citations) > 0:
            item.add_claims(citations)
        if string_citations is not None and len(string_citations) > 0:
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
    def __prepare_person_qualifiers__(self, person_object: Person):
        qualifiers = []
        if (
            person_object.given
            or person_object.given
            or person_object.orcid
            or person_object.number_in_sequence
        ) is not None:
            if person_object.given is not None:
                given_name = datatypes.String(
                    prop_nr=WCDProperty.GIVEN_NAME.value,
                    value=person_object.given,
                )
                qualifiers.append(given_name)
            if person_object.surname is not None:
                surname = datatypes.String(
                    prop_nr=WCDProperty.FAMILY_NAME.value,
                    value=person_object.surname,
                )
                qualifiers.append(surname)
            if person_object.number_in_sequence is not None:
                number_in_sequence = datatypes.Quantity(
                    prop_nr=WCDProperty.SERIES_ORDINAL.value,
                    amount=person_object.number_in_sequence,
                )
                qualifiers.append(number_in_sequence)
            if person_object.orcid is not None:
                orcid = datatypes.ExternalID(
                    prop_nr=WCDProperty.ORCID.value,
                    value=person_object.orcid,
                )
                qualifiers.append(orcid)
            if person_object.link is not None:
                link = datatypes.URL(
                    prop_nr=WCDProperty.URL.value,
                    value=person_object.link,
                )
                qualifiers.append(link)
            if person_object.mask is not None:
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
        logger.info("Preparing reference claims")
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
            value=str(wikipedia_page.revision_id),
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
        if page_reference.template_name is not None:
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
        if page_reference.access_date is not None:
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
        if page_reference.doi is not None:
            doi = datatypes.ExternalID(
                prop_nr=WCDProperty.DOI.value,
                value=page_reference.doi,
            )
        if page_reference.isbn_10 is not None:
            isbn_10 = datatypes.ExternalID(
                prop_nr=WCDProperty.ISBN_10.value,
                value=page_reference.isbn_10,
            )
        if page_reference.isbn_13 is not None:
            isbn_13 = datatypes.ExternalID(
                prop_nr=WCDProperty.ISBN_13.value,
                value=page_reference.isbn_13,
            )
        if page_reference.vauthors is not None:
            lumped_authors = datatypes.String(
                prop_nr=WCDProperty.LUMPED_AUTHORS.value,
                value=page_reference.vauthors,
            )
        if page_reference.orcid is not None:
            orcid = datatypes.ExternalID(
                prop_nr=WCDProperty.ORCID.value,
                value=page_reference.orcid,
            )
        if page_reference.pmid is not None:
            pmid = datatypes.ExternalID(
                prop_nr=WCDProperty.PMID.value,
                value=page_reference.pmid,
            )
        if page_reference.publication_date is not None:
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
        if page_reference.title is not None:
            title = datatypes.MonolingualText(
                prop_nr=WCDProperty.TITLE.value,
                text=page_reference.title,
                language=self.language_code,
            )
        if page_reference.url is not None:
            url = datatypes.URL(
                prop_nr=WCDProperty.URL.value,
                value=page_reference.url,
            )
        if page_reference.website is not None:
            website_string = datatypes.String(
                prop_nr=WCDProperty.WEBSITE_STRING.value,
                value=page_reference.website,
            )
        if page_reference.wikidata_qid is not None:
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
            lumped_authors,
            orcid,
            pmid,
            publication_date,
            retrieved_date,
            source_wikipedia,
            template_name,
            title,
            url,
            website_string,
            wikidata_qid,
        ):
            if claim is not None:
                claims.append(claim)
        return claims

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
        if (
            page_reference.authors_list is not None
            and len(page_reference.authors_list) > 0
        ):
            for author in page_reference.authors_list:
                if author.author_name_string is not None:
                    author = datatypes.String(
                        prop_nr=WCDProperty.AUTHOR_NAME_STRING.value,
                        value=author.author_name_string,
                    )
                    authors.append(author)
        if page_reference.vauthors is not None:
            author = datatypes.String(
                prop_nr=WCDProperty.LUMPED_AUTHORS.value,
                value=page_reference.vauthors,
            )
            authors.append(author)
        if page_reference.authors is not None:
            author = datatypes.String(
                prop_nr=WCDProperty.LUMPED_AUTHORS.value,
                value=page_reference.authors,
            )
            authors.append(author)
        if len(authors) == 0:
            authors = None
        return authors

    @staticmethod
    def __prepare_string_editors__(page_reference: WikipediaPageReference):
        persons = []
        if (
            page_reference.editors_list is not None
            and len(page_reference.editors_list) > 0
        ):
            for person in page_reference.editors_list:
                if person.author_name_string is not None:
                    person = datatypes.String(
                        prop_nr=WCDProperty.EDITOR_NAME_STRING.value,
                        value=person.author_name_string,
                    )
                    persons.append(person)
        else:
            persons = None
        return persons

    @staticmethod
    def __prepare_string_translators__(page_reference: WikipediaPageReference):
        persons = []
        if (
            page_reference.translators_list is not None
            and len(page_reference.translators_list) > 0
        ):
            for person in page_reference.translators_list:
                if person.author_name_string is not None:
                    person = datatypes.String(
                        prop_nr=WCDProperty.TRANSLATOR_NAME_STRING.value,
                        value=person.author_name_string,
                    )
                    persons.append(person)
        else:
            persons = None
        return persons

    def __prepare_string_citation_qualifiers__(
        self, page_reference: WikipediaPageReference
    ) -> List[Claim]:
        """Here we prepare all statements we normally
        would put on a unique separate page_reference item"""
        claims = []
        string_authors = self.__prepare_string_authors__(page_reference=page_reference)
        if string_authors is not None:
            claims.extend(string_authors)
        string_editors = self.__prepare_string_editors__(page_reference=page_reference)
        if string_editors is not None:
            claims.extend(string_editors)
        string_translators = self.__prepare_string_translators__(
            page_reference=page_reference
        )
        if string_translators is not None:
            claims.extend(string_translators)
        access_date = None
        archive_date = None
        archive_url = None
        publication_date = None
        title = None
        url = None
        website_string = None
        if page_reference.access_date is not None:
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
        if page_reference.archive_date is not None:
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
        if page_reference.archive_url is not None:
            archive_url = datatypes.URL(
                prop_nr=WCDProperty.ARCHIVE_URL.value,
                value=page_reference.archive_url,
            )
        if page_reference.publication_date is not None:
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
        if page_reference.title is not None:
            title = datatypes.MonolingualText(
                prop_nr=WCDProperty.TITLE.value,
                text=page_reference.title,
                language=self.language_code,
            )
        if page_reference.url is not None:
            url = datatypes.URL(
                prop_nr=WCDProperty.URL.value,
                value=page_reference.url,
            )
        if page_reference.website is not None:
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
            if claim is not None:
                claims.append(claim)
        return claims

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

    def __prepare_string_citations__(
        self, wikipedia_page: WikipediaPage
    ) -> Optional[List[Claim]]:
        # pseudo code
        # for each page_reference in the page that
        claims = []
        for page_reference in wikipedia_page.references:
            if not page_reference.has_hash:
                # generate string statements
                claims.append(
                    self.__prepare_string_citation__(page_reference=page_reference)
                )
        return claims

    @staticmethod
    def __setup_wbi__():
        wbi_config.config["USER_AGENT"] = "wcdimportbot"
        wbi_config.config["WIKIBASE_URL"] = config.wikibase_url
        wbi_config.config["MEDIAWIKI_API_URL"] = config.mediawiki_api_url
        wbi_config.config["MEDIAWIKI_INDEX_URL"] = config.mediawiki_index_url
        wbi_config.config["SPARQL_ENDPOINT_URL"] = config.sparql_endpoint_url

    def __upload_new_item__(self, item: ItemEntity) -> Optional[str]:
        if item is None:
            raise ValueError("Did not get what we need")
        if config.loglevel == logging.DEBUG:
            logger.debug("Finished item JSON")
            console.print(item.get_json())
            # exit()
        if config.cache_and_upload_enabled:
            new_item = item.write(summary="New item imported from Wikipedia")
            print(f"Added new item {self.entity_url(new_item.id)}")
            if config.press_enter_to_continue:
                input("press enter to continue")
            logger.debug(f"returning new wcdqid: {new_item.id}")
            return new_item.id
        else:
            print("skipped upload")

    def delete_all_page_and_reference_items(self):
        """This function deletes first the page item and then the reference items"""
        console.print("Deleting all imported items")
        self.__delete_all_page_items__()
        self.__delete_all_reference_items__()

    @validate_arguments
    def get_item(self, item_id: str) -> Optional[ItemEntity]:
        """Get one item from WikiCitations"""
        self.__setup_wbi__()
        wbi = WikibaseIntegrator()
        return wbi.item.get(item_id)

    @staticmethod
    @validate_arguments
    def entity_url(qid: str):
        return f"{config.wikibase_url}/wiki/Item:{qid}"

    @validate_arguments
    def prepare_and_upload_reference_item(
        self, page_reference: WikipediaPageReference, wikipedia_page: WikipediaPage
    ) -> str:
        self.__prepare_reference_claim__(wikipedia_page=wikipedia_page)
        item = self.__prepare_new_reference_item__(
            page_reference=page_reference, wikipedia_page=wikipedia_page
        )
        wcdqid = self.__upload_new_item__(item=item)
        return wcdqid

    @validate_arguments
    def prepare_and_upload_wikipedia_page_item(self, wikipedia_page: Any) -> str:
        logging.debug("prepare_and_upload_wikipedia_page_item: Running")
        from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

        if not isinstance(wikipedia_page, WikipediaPage):
            raise ValueError("did not get a WikipediaPage object")
        self.__prepare_reference_claim__(wikipedia_page=wikipedia_page)
        item = self.__prepare_new_wikipedia_page_item__(wikipedia_page=wikipedia_page)
        wcdqid = self.__upload_new_item__(item=item)
        return wcdqid
