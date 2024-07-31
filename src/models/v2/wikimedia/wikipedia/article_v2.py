import logging
import re
import pprint
# import urllib
from urllib.parse import quote, unquote

from datetime import datetime
from typing import Any, Dict, List, Optional
import json

import requests

# from pydantic import validate_arguments
from bs4 import BeautifulSoup
from dateutil.parser import isoparse

import config
from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.v2.base import IariBaseModel
from src.models.v2.job.article_job_v2 import ArticleJobV2
from src.models.v2.wikimedia.wikipedia.reference.extractor_v2 import (
    WikipediaReferenceExtractorV2,
)
from src.models.wikimedia.enums import WikimediaDomain

logger = logging.getLogger(__name__)


class WikipediaArticleV2(IariBaseModel):
    """Models a Wikimedia Wikipedia article

    Mediawiki specifics:
    * A page has a permanent and stable page_id
    * Every edit creates a new revision that is incremented across all pages to a specific page_id

    Implementation details:
    Cache setup occurs only in this class and
    not in the classes below (ie Website and WikipediaReference)
    because of
    https://github.com/internetarchive/wcdimportbot/issues/261"""

    job: ArticleJobV2
    extractor: Optional[WikipediaReferenceExtractorV2] = None

    new_article_data: Dict[str, Any] = {}

    references: List[Dict[str, Any]] = []
    ref_counter = 0

    url_dict: Dict[str, Any] = {}

    md5hash: Optional[str]
    page_id: int = 0
    wdqid: str = ""
    wikimedia_domain: WikimediaDomain = WikimediaDomain.wikipedia
    found_in_wikipedia: bool = True
    revision_isodate: Optional[datetime] = None
    revision_timestamp: int = 0

    wikitext: Optional[str]
    html_markup: Optional[str]

    ores_quality_prediction: str = ""
    ores_details: Dict = {}

    check_urls: bool = False
    testing: bool = False
    debug_info: Dict[str, Any] = {}

    error_items: List[Any] = []

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable
        extra = "forbid"  # dead: disable

    @property
    def parse_errors(self) -> List[Any]:
        return self.error_items

    @property
    def is_redirect(self) -> bool:
        return "#REDIRECT" in str(self.wikitext)[:10]

    @property
    def reference_count(self) -> int:
        return len(self.references)

    @property
    def reference_stats(self) -> Dict[str, Any]:
        counts = {}
        for ref in self.references:
            if "source_section" in ref:
                source_section = ref["source_section"]
                if source_section not in counts:
                    counts[source_section] = 0
                counts[source_section] += 1

        return {"sections": counts}

    @property
    def url_count(self) -> int:
        return len(self.urls)

    @property
    def url_stats(self) -> Dict[str, Any]:
        return {
            "fld_counts": {}
        }

    @property
    def urls(self) -> List[str]:
        urls = []
        for key, value in self.url_dict.items():
            urls.append(key)
        return urls

    @property
    def revision_id(self) -> int:
        return self.job.revision or 0

    @property
    def url(self):
        return self.job.url

    def fetch_and_parse(self):
        """
        fetch embellished html for article
        parse this html for articles, etc.
        """
        from src import app

        app.logger.debug("==> ArticleV2::fetch_and_parse")
        app.logger.info("Fetching article data and parsing")

        if not self.wikitext:
            # fetch page data from Wikipedia if we don't already have wikitext
            # WTF why would we not have this?
            self.__fetch_wikitext__()

        if self.is_redirect:
            logger.debug(
                "Skipped extraction and parsing because the article is a redirect"
            )
            raise WikipediaApiFetchError("wiki article is a redirect")

        if not self.found_in_wikipedia:
            logger.debug(
                "Skipped extraction and parsing because the article was not found"
            )
            raise WikipediaApiFetchError("wiki article not found in wiki")

        if not self.wikitext:
            raise WikipediaApiFetchError("wikitext is empty")


        # wikitext extraction

        app.logger.debug("==> ArticleV2::fetch_and_parse: extracting from wikitext")

        # elif not self.is_redirect and self.found_in_wikipedia:
        if not self.is_redirect and self.found_in_wikipedia:

            if not self.wikitext:
                raise MissingInformationError("WikipediaReferenceExtractorV2::fetch_and_parse: self.wikitext is empty")

            app.logger.debug("==> ArticleV2::fetch_and_parse: setting extractor")

            self.extractor = WikipediaReferenceExtractorV2(
                wikitext=self.wikitext,
                html_source=self.html_markup,
                job=self.job,
            )

            # raise MissingInformationError("HoHum!")

            app.logger.debug("==> ArticleV2::fetch_and_parse: extracting all refs")
            self.extractor.extract_all_references()

            app.logger.debug("==> ArticleV2::fetch_and_parse: fetching ores scores")
            self.__get_ores_scores__()
            # self.__generate_hash__()


        app.logger.debug("==> ArticleV2::fetch_and_parse: extracting from html")

        # html extraction
        if not self.html_markup:
            self.__fetch_html__()

        self.__extract_footnote_references__()
        self.__extract_section_references__()
        self.__extract_urls_from_references__()

        self.__get_ores_scores__()  # fills ores_quality_prediction and ores_details

    def __extract_urls_from_references__(self):
        # traverse references, adding urls to self.urlDict,
        from src import app
        for ref in self.references:
            for url in ref["template_urls"]:
                if url == "":
                    app.logger.debug(f"EMPTY URL FOUND, wiki_ref_id: {ref['wiki_ref_id']}")
                    self.error_items.append( {
                        "type": "template_url_extraction",
                        "error": "empty URL found in template_urls",
                        "id": f"wiki_ref_id {ref['wiki_ref_id']}"
                    })
                if url not in self.url_dict:
                    self.url_dict[url] = {
                        "count": 0,
                        "refs": [ref["ref_id"]]
                    }

                app.logger.debug(f"Adding {url} to urlDict")
                self.url_dict[url]["count"] += 1
                self.url_dict[url]["refs"].append(ref["ref_id"])

    def __extract_footnote_references__(self):
        """
        references|
        bibliography|Bibliography
        further reading|Further_reading
        works cited| ** still need example
        sources| ** still need example
        external links|External_links
        """

        regex_extract_ref_name = r"#cite_note-(.*?)-\d+$"

        soup = BeautifulSoup(self.html_markup, "html.parser")
            # for link in soup.find_all("a"):
            #     print(link.get("href"))


        references_wrapper = soup.find("div", class_="mw-references-wrap")

        refs = []

        if references_wrapper:
            references_list = references_wrapper.find("ol", class_="references")
            for ref in references_list.find_all("li"):

                self.ref_counter += 1

                # collect cite refs back to article location
                page_refs = []
                for link in ref.find_all("a"):
                    # span.mw-linkback-text children should have a citeref link
                    if link.find("span", class_="mw-linkback-text"):
                        page_refs.append(
                            {
                                "href": link.get("href"),
                                "id": link.get("id"),
                            }
                        )

                # extract templates
                templates = []
                span_templates = []
                cite_html = None
                span_html = None
                urls = []
                template_urls = []
                ref_info = {
                    "about_link": "",
                    "ref_name": "",
                    "cite_id": "",
                    "cite_class": "",
                }

                from src import app

                ref_info["about_link"] = ref.get("about")
                match = re.search(regex_extract_ref_name, ref_info["about_link"])
                if match:
                    ref_info["ref_name"] = match.group(1)

                span_ref = ref.find("span", class_="mw-reference-text")
                if span_ref:
                    # span_ref contains citation markup and possible template data

                    app.logger.debug(f"Checking <link> data...")

                    # fetch "template" data from link[data-mw] attribute
                    link_refs = span_ref.find_all("link")
                    # typeof="mw:Extension/templatestyles mw:Transclusion"
                    # skip if typeof="mw:Extension/templatestyles"

                    # append templates with data from link_refs, if any
                    for link_ref in link_refs:
                        template_data = link_ref.get("data-mw")
                        if template_data:
                            template = self.__parse_template__(template_data)
                            if template:
                                templates.append(template)

                    # extract template urls
                    for template in templates:
                        if "parameters" in template:
                            if "url" in template["parameters"]:
                                template_urls.append(template["parameters"]["url"])
                            # if template["params"]["archive-url"]:
                            #     template_urls.append(template["params"]["url"])

                    # extract entire <cite> html
                    cite = span_ref.find("cite")

                    if cite:
                        cite_html = cite.prettify()
                        # extract urls from <a> tags from <cite>
                        a_tags = cite.find_all('a')
                        # urls = [a.get('href') for a in a_tags]
                        for a in a_tags:
                            href = a.get('href')
                            if re.match(r"^https?://", href) is not None:
                                urls.append(href)

                        ref_info["cite_id"] = cite.get("id")
                        ref_info["cite_class"] = cite.get("class")

                    else:  # no cite found, use span as reference text
                        pass
                        
                    # fetch other "template" data from span.Z3988[title] attribute
                    # TODO What is held in these elements, specifically? is it books?
                    span_refs = span_ref.find_all("span", class_="Z3988")
                    for span_ref in span_refs:
                        app.logger.debug(f"found span.Z3988...")
                        span_data = span_ref.get("title")
                        if span_data:
                            span_template = self.__parse_span_template__(span_data)
                            if span_template:
                                span_templates.append(span_template)

                # extract any other templates from alternative template structures
                # TODO fill in code here...there are other template things

                # if cite_html was not found, use span_ref as html source...
                if not cite_html:
                    span_html = span_ref.prettify()


                # accumulate template_names
                template_names = []
                for template in templates:
                    if "name" in template:
                        template_names.append(template["name"])


                # push the details for the reference
                refs.append(
                    {
                        "wiki_ref_id": ref.get("id"),
                        "ref_id": self.ref_counter,
                        "source_section": "References",  # which section these refs are from
                        "cite_def_link": ref.get("about"),
                        "cite_ref_links": page_refs,
                        "template_names": template_names,
                        "templates": templates,
                        "urls": urls,
                        "template_urls": template_urls,
                        "span_templates": span_templates,
                        "cite_html": cite_html,
                        "span_html": span_html,
                        "ref_info": ref_info,
                    }
                )

        self.references.extend(refs)

    def __extract_section_references__(self):

        soup = BeautifulSoup(self.html_markup, "html.parser")
            # for link in soup.find_all("a"):
            #     print(link.get("href"))

        sections = soup.find_all('section')

        # Iterate through sections to find the one with child of interest
        for section in sections:
            if section.find('h2', id='Bibliography'):
                self.__extract_section_refs__(section, 'Bibliography')
                # break
            if section.find('h2', id='Further_reading'):
                self.__extract_section_refs__(section, 'Further_reading')
                # break

            # we could do other sections here:
            # id-'Further_reading'
            # id-'External_links'

    def __extract_section_refs__(self, section, section_id):
        if not section:
            return

        refs = []

        ref_list = section.find("ul")
        if ref_list:
            for ref in ref_list.find_all("li"):
                """
                at this point, <link>, <cite>, and <span> sub elements are present
                """
                self.ref_counter += 1
                templates = []
                urls = []
                template_urls = []
                cite_html = ""

                # extract templates
                link_refs = ref.find_all("link")
                for link_ref in link_refs:
                    template_data = link_ref.get("data-mw")
                    if template_data:
                        template = self.__parse_template__(template_data)
                        if template:
                            templates.append(template)

                # extract template urls
                for template in templates:
                    if "parameters" in template:
                        if "url" in template["parameters"]:
                            template_urls.append(template["parameters"]["url"])
                        # if template["params"]["archive-url"]:
                        #     template_urls.append(template["params"]["url"])

                # extract entire <cite> html
                cite = ref.find("cite")
                if cite:
                    cite_html = cite.prettify()
                    # extract urls from <a> tags from <cite>
                    a_tags = cite.find_all('a')
                    # urls = [a.get('href') for a in a_tags]
                    for a in a_tags:
                        href = a.get('href')
                        if re.match(r"^https?://", href) is not None:
                            urls.append(href)

                # accumulate template_names
                template_names = []
                for template in templates:
                    if "name" in template:
                        template_names.append(template["name"])

                # push the details for the reference
                refs.append(
                    {
                        "wiki_ref_id": ref.get("id"),  # TODO this should come from cite
                        "ref_id": self.ref_counter,
                        "source_section": section_id,  # which section these refs are from
                        "cite_ref_link": "",  # ref.get("about"),
                        "cite_def_links": [],  # page_refs,
                        "template_names": template_names,
                        "templates": templates,
                        "urls": urls,
                        "template_urls": template_urls,
                        "span_templates": [],  # span_templates,
                        "cite_html": cite_html,
                    }
                )

        self.references.extend(refs)

    # xxx@staticmethod
    # noinspection PyMethodMayBeStatic
    def __parse_template__(self, template_data) -> Dict[str, Any] or None:
        """
        1. remove outer quotes, if any
        2. parse into "small tree"
        3. peruse tree and make "big tree"
        """
        json_string_to_parse = template_data.strip('\'')  # remove beginning and ending quotes
        ref_dict = json.loads(json_string_to_parse)

        # from src import app
        # app.logger.debug(pprint.pformat(ref_dict))

        parts = ref_dict.get("parts")
        template = None
        if parts and len(parts) > 0:
            part = parts[0]  # just get first part for now (don't know if there are ever more)
            my_template = part.get("template")
            if my_template:
                template = {}

                if "target" in my_template and "wt" in my_template["target"]:
                    template["name"] = my_template["target"]["wt"].strip()

                my_params = my_template["params"]
                if my_params:
                    params = {}
                    for key in my_params:
                        params[key] = my_params[key]["wt"]
                    template["parameters"] = params

        return template

    # xxx@staticmethod
    # noinspection PyMethodMayBeStatic
    def __parse_span_template__(self, span_data) -> Dict[str, Any] or None:
        """
        1. parse elements into list
            a. separate by &amp; and put into list
        2. traverse list for info
        ? is this the template data for non-cs1 templates?

        title="ctx_ver=Z39.88-2004
        &amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal
        &amp;rft.genre=unknown&amp;rft.jtitle=National+Statistics+Institute
        &amp;rft.atitle=Censo+de+Poblaci%C3%B3n+y+Vivienda+2002
        &amp;rft_id=http%3A%2F%2Fwww.ine.cl%2Fcanales%2Fchile_estadistico%2Fcensos_poblacion_vivienda%2Fcenso_pobl_vivi.php&amp;rfr_id=info%3Asid%2Fen.wikipedia.org%3AEaster+Island"

        <span title="ctx_ver=Z39.88-2004&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal&amp;rft.genre=unknown&amp;rft.jtitle=National+Statistics+Institute&amp;rft.atitle=Censo+de+Poblaci%C3%B3n+y+Vivienda+2002&amp;rft_id=http%3A%2F%2Fwww.ine.cl%2Fcanales%2Fchile_estadistico%2Fcensos_poblacion_vivienda%2Fcenso_pobl_vivi.php&amp;rfr_id=info%3Asid%2Fen.wikipedia.org%3AEaster+Island"
              class="Z3988"
              id="mwBaI"></span>

        """
        from src import app

        # app.logger.debug(f"span_data: {span_data}")

        span_list = span_data.split("&")

        app.logger.debug(f"SPAN DATA (parsed):")

        span_template = []
        # print this string out
        for elem in span_list:
            # app.logger.debug(f"span element: {elem}")
            val = elem

            # replace "+" with space
            val = val.replace("+", " ")
            val = unquote(val)

            span_template.append(val)

        return span_template

    def __fetch_wikitext__(self) -> None:
        """This fetches metadata and the latest revision id
        and date from the MediaWiki REST v1 API if needed"""
        from src import app

        app.logger.debug("WikipediaArticleV2::__fetch_wikitext__")
        self.__check_if_title_is_empty__()
        if not self.wikitext:
            if self.revision_id:
                self.__fetch_data_for_specific_revision__()
            else:
                self.__fetch_data_for_latest_revision__()

        else:
            logger.info(
                "Not fetching data via the Wikipedia REST API. We have already got all the data we need"
            )

    def __fetch_html__(self) -> None:
        """This fetches metadata and the latest revision id
        and date from the MediaWiki REST v1 API if needed"""
        from src import app

        app.logger.debug("WikipediaArticleV2::__fetch_html__")
        self.__check_if_title_is_empty__()

        # fetch html page data - sets self.html_markup
        self.__fetch_page_html__(self.revision_id)

    def __check_if_title_is_empty__(self):
        if not self.job.title:
            raise MissingInformationError("self.job.title was empty string")

    def __get_ores_scores__(self):
        from src import app

        if not self.revision_id:
            raise MissingInformationError("__get_ores_scores__: No revision_id provided.")
            # if self.job.testing:
            #     logger.warning(
            #         "Not testing getting ores score during testing "
            #         "when no revision_id or latest_revision_id are present"
            #     )
            # else:
            #     raise MissingInformationError("__get_ores_scores__: No revision_id provided.")
        else:
            # get the latest ORES score via ORES API:
            #   https://ores.wikimedia.org/v3/scores/enwiki/234234320/articlequality
            # We only support Wikipedia for now
            wiki_project = f"{self.job.lang}wiki"
            response = requests.get(
                f"https://ores.wikimedia.org/v3/scores/"
                f"{wiki_project}/{self.revision_id}/articlequality"
            )
            if response.status_code == 200:
                data = response.json()
                # console.print(data)
                string_id = str(self.revision_id)

                self.ores_quality_prediction \
                    = data[wiki_project]["scores"][string_id]["articlequality"]["score"]["prediction"]
                self.ores_details = data[wiki_project]["scores"][
                    string_id]["articlequality"]["score"]

            else:
                app.logger.debug("Error:", response.status_code)

    def __fetch_data_for_specific_revision__(self):
        """Get wikitext for a specific revision

        Action-specific parameters

        titles= takes one or more titles for the query to operate on.

        pageids= takes one or more page ids for the query to operate on. revids= takes a list of revision IDs to work on.
        """
        from src import app

        app.logger.debug("__fetch_data_for_specific_revision__: running")
        url = (
            f"https://{self.job.lang}.{self.job.domain.value}/"
            f"w/rest.php/v1/revision/{self.job.revision}"
        )

        prop = "ids|timestamp|content"
        headers = {"User-Agent": config.user_agent}
        response = requests.get(
            url, params={"action": "query", "prop": prop}, headers=headers
        )
        # console.print(response.json())
        if response.status_code == 200:
            app.logger.debug("returned article data with prop: ids|timestamp|content")

            data = response.json()
            # self.revision_timestamp = data["timestamp"]
            self.revision_isodate = isoparse(data["timestamp"])
            self.revision_timestamp = round(self.revision_isodate.timestamp())
            self.page_id = data["page"]["id"]
            # logger.debug(f"Got pageid: {self.page_id}")
            self.wikitext = data["source"]

        elif response.status_code == 404:
            self.found_in_wikipedia = False
            logger.error(
                f"Could not fetch page data from {self.wikimedia_domain.name} because of 404. See {url}"
            )
        else:
            raise WikipediaApiFetchError(
                f"Could not fetch page data. Got {response.status_code} from {url}"
            )

    def __fetch_data_for_latest_revision__(self):
        # This is needed to support e.g. https://en.wikipedia.org/wiki/Musk%C3%B6_naval_base or
        # https://en.wikipedia.org/wiki/GNU/Linux_naming_controversy
        from src import app

        url = (
            f"https://{self.job.lang}.{self.job.domain.value}/"
            f"w/rest.php/v1/page/{self.job.quoted_title}"
        )
        headers = {"User-Agent": config.user_agent}
        response = requests.get(url, headers=headers)
        # console.print(response.json())
        if response.status_code == 200:
            data = response.json()
            self.job.revision = int(data["latest"]["id"])
            self.revision_isodate = isoparse(data["latest"]["timestamp"])
            self.revision_timestamp = round(self.revision_isodate.timestamp())
            self.page_id = int(data["id"])
            # logger.debug(f"Got pageid: {self.page_id}")
            self.wikitext = data["source"]

        elif response.status_code == 404:
            self.found_in_wikipedia = False
            app.logger.error(
                f"Could not fetch page data from {self.wikimedia_domain.name} because of 404. See {url}"
            )
        else:
            raise WikipediaApiFetchError(
                f"Could not fetch page data. Got {response.status_code} from {url}"
            )

    def __fetch_page_html__(self, revision_id=0):
        """
        Get html for wiki page as specified by
        """
        from src import app

        app.logger.debug(
            f"WikipediaArticleV2::__fetch_page_html__, revision_id is {revision_id}"
        )

        # example request url for html source:
        # https://en.wikipedia.org/w/rest.php/v1/page/Earth/with_html
        url = (
            f"https://{self.job.lang}.{self.job.domain.value}/"
            f"w/rest.php/v1/page/{self.job.quoted_title}/with_html"
        )

        headers = {"User-Agent": config.user_agent}
        response = requests.get(url, headers=headers)

        # console.print(response.json())
        if response.status_code == 200:

            data = response.json()
            self.html_markup = data["html"]

        elif response.status_code == 404:
            # self.found_in_wikipedia = False
            logger.error(
                f"Could not fetch page html from {self.wikimedia_domain.name} because of 404. See {url}"
            )
            # NB TODO how to error here?
        else:
            raise WikipediaApiFetchError(
                f"Could not fetch page html. Got {response.status_code} from {url}"
            )
            # NB TODO how to error here?
