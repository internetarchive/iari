import re
from urllib.parse import quote, unquote
#
# import requests
#
# import config
# from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.wikimedia.enums import WikimediaDomain
from src import MissingInformationError
from src.models.v2.job import JobV2


class EditRefJobV2(JobV2):
    """job that supports EditRefV2 endpoint"""

    old_ref: str = ""
    new_ref: str = ""

    source: str = ""
    wiki_page_url: str = ""

    wiki_lang: str = ""
    wiki_domain: WikimediaDomain = WikimediaDomain.wikipedia
    wiki_page_title: str = ""
    wiki_revision: str = ""

    regex_wiki_url = r"https?://(\w+)\.(\w+\.\w+)/wiki/(.+)"
    # NB this should be elevated to a globalish constant

    @property
    def quoted_title(self):
        if not self.wiki_page_title:
            raise MissingInformationError("self.wiki_page_title is empty")
        return quote(self.wiki_page_title, safe="")

    # these following (commented) functions might be useful when we
    # have a wikipage id rather than a string to describe source

    # def get_mediawiki_ids(self) -> None:
    #     from src import app
    #
    #     app.logger.debug(
    #         f"ArticleJobV2::get_mediawiki_ids: self.page_id={self.page_id}"
    #     )
    #
    #     if not self.page_id:
    #         app.logger.debug(
    #             f"ArticleJobV2::get_mediawiki_ids: lang={self.lang}, title={self.title}, lang={self.domain}"
    #         )
    #         if not self.lang or not self.title or not self.domain:
    #             raise MissingInformationError("url lang, title or domain not found")
    #
    #         # https://stackoverflow.com/questions/31683508/wikipedia-mediawiki-api-get-pageid-from-url
    #         wiki_fetch_url = (
    #             f"https://{self.lang}.{self.domain.value}/"
    #             f"w/rest.php/v1/page/{self.quoted_title}"
    #         )
    #         headers = {"User-Agent": config.user_agent}
    #         response = requests.get(wiki_fetch_url, headers=headers)
    #         # console.print(response.json())
    #         if response.status_code == 200:
    #             data = response.json()
    #             # We only set this if the patron did not specify a revision they want
    #             if not self.revision:
    #                 self.revision = int(data["latest"]["id"])
    #             self.page_id = int(data["id"])
    #
    #         elif response.status_code == 404:
    #             app.logger.error(
    #                 f"Could not fetch page data from {self.domain} because of 404. See {wiki_fetch_url}"
    #             )
    #         else:
    #             raise WikipediaApiFetchError(
    #                 f"Could not fetch page data. Got {response.status_code} from {wiki_fetch_url}"
    #             )

    # def __urldecode_url__(self):
    #     """We decode the title to have a human readable string to pass around"""
    #     self.url = unquote(self.url)
    #
    # def __extract_url__(self):
    #     """This was generated with help of chatgpt using this prompt:
    #     I want a python re regex that extracts "en" "wikipedia.org"
    #     and "Test" from http://en.wikipedia.org/wiki/Test
    #     """
    #     from src import app
    #
    #     app.logger.debug("extract_url: running")
    #     if self.url:
    #         self.__urldecode_url__()
    #         wiki_url_pattern = r"https?://(\w+)\.(\w+\.\w+)/wiki/(.+)"
    #
    #         matches = re.match(wiki_url_pattern, self.url)
    #         if matches:
    #             groups = matches.groups()
    #             self.lang = groups[0]
    #             self.domain = WikimediaDomain(groups[1])
    #             self.title = groups[2]
    #         if not matches:
    #             app.logger.error("Not a supported Wikimedia URL")

    def validate_fields(self):
        """
        any parameter checking done here...

        must have at least "source" or "wiki_page_url" defined
        """

        from src import app

        if not self.source:
            if not self.wiki_page_url:
                app.logger.error('Parameters must contain a valid "source" or valid "wiki_page_url" value. '
                                 f"source: {self.source}, wiki_page_url: {self.wiki_page_url}")
                raise MissingInformationError(
                    f'Parameters must contain a valid "source" or valid "wiki_page_url" value.'
                )

            # extract wiki parts from wiki_page_url?
            my_url = unquote(self.wiki_page_url)

            matches = re.match(self.regex_wiki_url, my_url)
            if matches:
                groups = matches.groups()
                self.wiki_lang = groups[0]
                self.wiki_domain = WikimediaDomain(groups[1])
                self.wiki_page_title = groups[2]
            else:
                app.logger.error(f"{self.wiki_page_url} is not a supported Wikimedia URL")
                raise MissingInformationError(
                    f"wiki_page_url parameter value ({self.wiki_page_url}) is invalid."
                )

