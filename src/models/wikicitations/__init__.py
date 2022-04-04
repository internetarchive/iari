import logging
from datetime import datetime, timezone
from typing import Any, Optional, List

from pydantic import BaseModel, validate_arguments
from wikibaseintegrator import wbi_config, datatypes, WikibaseIntegrator, wbi_login
from wikibaseintegrator.entities import ItemEntity
from wikibaseintegrator.models import Claim

import config
from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage
from src.models.wikicitations.enums import WCDProperty, WCDItem
from src.models.wikimedia.wikipedia.templates.wikipedia_page_reference import (
    WikipediaPageReference,
)

logger = logging.getLogger(__name__)


class WikiCitations(BaseModel):
    """This class models the WikiCitations Wikibase and handles all uploading to it

    We want to create items for all Wikipedia pages and references with a unique hash"""

    @staticmethod
    def __prepare_authors__(
        page_reference: WikipediaPageReference,
    ) -> Optional[List[Claim]]:
        authors = []
        if page_reference.authors is not None and len(page_reference.authors) > 0:
            for author in page_reference.authors:
                author = datatypes.String(
                    prop_nr=WCDProperty.AUTHOR_NAME_STRING.value,
                    value=author.author_name_string,
                )
                authors.append(author)
        else:
            authors = None
        return authors

    @staticmethod
    def __prepare_citations__(wikipedia_page: WikipediaPage) -> Optional[List[Claim]]:
        # pseudo code
        # for each page_reference in the page
        claims = []
        for reference in wikipedia_page.references:
            if reference.wikicitations_qid is not None:
                citation = datatypes.Item(
                    prop_nr=WCDProperty.CITATIONS.value,
                    value=reference.wikicitations_qid,
                )
                claims.append(citation)
        return claims

    @validate_arguments
    def __prepare_new_wikipedia_page_item__(
        self, wikipedia_page: WikipediaPage
    ) -> ItemEntity:
        """This method converts a page_reference into a new WikiCitations item"""
        self.__setup_wbi__()
        wbi = WikibaseIntegrator(
            login=wbi_login.Login(user=config.user, password=config.pwd),
        )
        item = wbi.item.new()
        item.labels.set("en", wikipedia_page.pywikibot_page.title)
        item.descriptions.set(
            "en", f"page from {wikipedia_page.wikimedia_site.name.title()}"
        )
        # Prepare claims
        # First prepare the page_reference needed in other claims
        citations = self.__prepare_citations__(wikipedia_page=wikipedia_page)
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
            logger.debug("Printing the item json")
            print(item.get_json())
            exit()
        return item

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
        # Prepare claims
        # First prepare the page_reference needed in other claims
        authors = self.__prepare_authors__(page_reference=page_reference)
        if authors is not None:
            item.add_claims(authors)
        item.add_claims(
            self.__prepare_single_value_reference_claims__(
                page_reference=page_reference
            ),
        )
        if config.loglevel == logging.DEBUG:
            logger.debug("Printing the item json")
            print(item.get_json())
            exit()
        return item

    @staticmethod
    def __prepare_reference_claim__() -> List[Claim]:
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
        claims = []
        for claim in (retrieved_date,):
            if claim is not None:
                claims.append(claim)
        return claims

    @staticmethod
    def __prepare_single_value_reference_claims__(
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
        # We hardcode enWP for now
        source_wikipedia = datatypes.Item(
            prop_nr=WCDProperty.SOURCE_WIKIPEDIA.value,
            value=WCDItem.ENGLISH_WIKIPEDIA.value,
        )
        hash = datatypes.String(
            prop_nr=WCDProperty.HASH.value, value=page_reference.md5hash
        )
        # Optional claims
        doi = None
        isbn_10 = None
        isbn_13 = None
        orcid = None
        pmid = None
        publication_date = None
        template_name = None
        title = None
        url = None
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
                value=(
                    page_reference.publication_date.replace(tzinfo=timezone.utc)
                    .replace(
                        hour=0,
                        minute=0,
                        second=0,
                    )
                    .strftime("+%Y-%m-%dT%H:%M:%SZ"),
                ),
            )
        if page_reference.title is not None:
            title = datatypes.MonolingualText(
                prop_nr=WCDProperty.TITLE.value,
                text=page_reference.title,
                # FIXME avoid hardcoding here
                language="en",
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
        claims = []
        for claim in (
            doi,
            hash,
            instance_of,
            isbn_10,
            isbn_13,
            orcid,
            pmid,
            publication_date,
            source_wikipedia,
            template_name,
            title,
            url,
            website_string,
        ):
            if claim is not None:
                claims.append(claim)
        return claims

    @staticmethod
    def __prepare_single_value_wikipedia_page_claims__(wikipedia_page) -> List[Claim]:
        # There are no optional claims for Wikipedia Pages
        absolute_url = datatypes.URL(
            prop_nr=WCDProperty.URL.value,
            value=wikipedia_page.absolute_url,
        )
        hash = datatypes.String(
            prop_nr=WCDProperty.HASH.value, value=wikipedia_page.md5hash
        )
        page_id = datatypes.String(
            prop_nr=WCDProperty.MEDIAWIKI_PAGE_ID.value,
            value=str(wikipedia_page.page_id),
        )
        published_in = datatypes.Item(
            prop_nr=WCDProperty.PUBLISHED_IN.value,
            value=WCDItem.ENGLISH_WIKIPEDIA.value,
        )
        title = datatypes.String(
            prop_nr=WCDProperty.TITLE.value,
            value=wikipedia_page.title,
        )
        return [absolute_url, hash, page_id, published_in, title]

    @staticmethod
    def __prepare_string_authors__(page_reference: WikipediaPageReference):
        authors = []
        if page_reference.authors is not None and len(page_reference.authors) > 0:
            for author in page_reference.authors:
                author = datatypes.String(
                    prop_nr=WCDProperty.AUTHOR_NAME_STRING.value,
                    value=author.author_name_string,
                )
                authors.append(author)
        else:
            authors = None
        return authors

    def __prepare_string_citation_qualifiers__(
        self, page_reference: WikipediaPageReference
    ):
        """Here we prepare all statements we normally
        would put on a unique separate page_reference item"""
        # TODO support more fields
        claims = []
        string_authors = self.__prepare_string_authors__(page_reference=page_reference)
        if string_authors is not None:
            claims.extend(string_authors)
        publication_date = None
        title = None
        url = None
        website_string = None
        if page_reference.publication_date is not None:
            publication_date = datatypes.Time(
                prop_nr=WCDProperty.PUBLICATION_DATE.value,
                value=(
                    page_reference.publication_date.replace(tzinfo=timezone.utc)
                    .replace(
                        hour=0,
                        minute=0,
                        second=0,
                    )
                    .strftime("+%Y-%m-%dT%H:%M:%SZ"),
                ),
            )
        if page_reference.title is not None:
            title = datatypes.String(
                prop_nr=WCDProperty.TITLE.value,
                value=page_reference.title,
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
            hash,
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
        string_citation = datatypes.Item(
            prop_nr=WCDProperty.STRING_CITATIONS.value,
            value=page_reference.template_name,
            qualifiers=self.__prepare_string_citation_qualifiers__(
                page_reference=page_reference
            ),
        )
        return string_citation

    def __prepare_string_citations__(
        self, wikipedia_page: WikipediaPage
    ) -> Optional[List[Claim]]:
        # pseudo code
        # for each page_reference in the page that
        claims = []
        for reference in wikipedia_page.references:
            if not reference.has_hash:
                # generate string statements
                claims.append(
                    self.__prepare_string_citation__(page_reference=reference)
                )
        return claims

    @staticmethod
    def __setup_wbi__():
        wbi_config.config["WIKIBASE_URL"] = config.wikibase_url
        wbi_config.config["MEDIAWIKI_API_URL"] = config.mediawiki_api_url
        wbi_config.config["MEDIAWIKI_INDEX_URL"] = config.mediawiki_index_url
        wbi_config.config["SPARQL_ENDPOINT_URL"] = config.sparql_endpoint_url

    def __upload_new_item__(self, item: ItemEntity) -> Optional[str]:
        if item is None:
            raise ValueError("Did not get what we need")
        if config.upload_enabled:
            new_item = item.write(summary="New item imported from Wikipedia")
            print(f"Added new item {self.entity_url(new_item.id)}")
            if config.press_enter_to_continue:
                input("press enter to continue")
            return new_item.id
        else:
            print("skipped upload")

    @validate_arguments
    def prepare_and_upload_reference_item(
        self, page_reference: WikipediaPageReference, wikipedia_page: WikipediaPage
    ) -> WikipediaPageReference:
        item = self.__prepare_new_reference_item__(
            page_reference=page_reference, wikipedia_page=wikipedia_page
        )
        page_reference.wikicitations_qid = self.__upload_new_item__(item=item)
        return page_reference

    @validate_arguments
    def prepare_and_upload_wikipedia_page_item(
        self, wikipedia_page: Any
    ) -> WikipediaPage:
        from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

        if not isinstance(wikipedia_page, WikipediaPage):
            raise ValueError("did not get a WikipediaPage object")
        item = self.__prepare_new_wikipedia_page_item__(wikipedia_page=wikipedia_page)
        wikipedia_page.wikicitations_qid = self.__upload_new_item__(item=item)
        return wikipedia_page

    @staticmethod
    def entity_url(qid):
        return f"{wbi_config.config['WIKIBASE_URL']}/wiki/{qid}"
