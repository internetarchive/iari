# from flask_restful import Resource, abort  # type: ignore
# from marshmallow import Schema
from datetime import datetime
from typing import Any, Optional, Tuple, List, Dict
import traceback

from dateutil.parser import isoparse

import config
import requests

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.v2.job.article_job_v2 import ArticleJobV2

from src.models.v2.schema.fetchrefs_schema_v2 import FetchRefsSchemaV2
from src.models.v2.job.fetchrefs_job_v2 import FetchRefsJobV2
# from src.models.v2.wikimedia.wikipedia.wiki_page_v2 import WikiArticleV2

from src.models.api.job.article_job import ArticleJob
from src.models.v2.wikimedia.wikipedia.article_v2 import WikipediaArticleV2
from src.models.wikimedia.wikipedia.article import WikipediaArticle

from src.views.v2.statistics import StatisticsViewV2
from src.models.wikimedia.enums import RequestMethods


class FetchRefsV2(StatisticsViewV2):

    """
    takes an array of page specifiers, and
    returns data for all citations for each page.

    """

    schema = FetchRefsSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: FetchRefsJobV2           # Holds usable variables, seeded from schema. Overrides StatisticsViewV2's "job"

    pages: List[Dict[str, Any]] = []  # contents parsed from pipe-delimited "pages" URL parameter

    def get(self):
        """
        flask GET entrypoint for returning fetchrefs results
        must return a tuple: (Any,response_code)
        """
        from src import app
        app.logger.debug(f"==> FetchRefsV2::get")

        return self.__process_request__(method=RequestMethods.get)
        # return {"errors": [
        #     {"error": "GET method not supported for this endpoint"}
        # ]}

    def post(self):
        """
        flask POST entrypoint for returning fetchrefs results
        must return a tuple: (Any,response_code)
        """
        from src import app
        app.logger.debug(f"==> FetchRefsV2::post")

        # return self.__process_data__(method="post")
        return self.__process_request__(method=RequestMethods.post)


    def __process_request__(self, method=RequestMethods.post):  # default to POST
        # populate local "pages" property
        from src import app
        app.logger.debug(f"==> FetchRefsV2::__process_request__, method = {method}")

        try:
            self.__validate_and_get_job__(method)  # inherited from StatisticsViewV2

            self.pages = []

            # process pages, get refs, sets self.pages data
            for page in self.job.pages:
                page_results = self.__get_page_data__(page)
                # append page ref data to pages result
                self.pages.append(page_results)

            # and return results
            return {"pages": self.pages}


        except MissingInformationError as e:
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500

    def __get_page_data__(self, page_title):
        """
        Assume page is a fully resolved url, such as: https://en.wikipedia.org/wiki/Easter_Island
        """

        try:
            # process page

            url_template = "https://{lang}.{wiki_domain}/wiki/{page_title}"  # TODO make this a global
            page_url = url_template.format(page_title=page_title, lang="en", wiki_domain="wikipedia.org")

            article_job = ArticleJobV2(url=page_url)
            article_job.__extract_url__()

            # get article object corresponding to page
            # page = WikiArticleV2(job=article_job)

            page = WikipediaArticleV2(job=article_job)
            page.fetch_and_parse()

            # loop thru references
            page_refs = []
            if page.extractor:
                for ref in page.extractor.references:
                    page_refs.append({
                        "name": ref.get_name,
                        "wikitext": ref.wikicode_as_string
                    })

        except WikipediaApiFetchError as e:
            return {
                "page_title": page_title,
                "which_wiki": self.job.which_wiki,
                "error": f"Page data error: {str(e)}"
            }

        except Exception as e:
            traceback.print_exc()
            return {
                "page_title": page_title,
                "which_wiki": self.job.which_wiki,
                "error": f"General error: {str(e)}"
            }

        return {
            "page_title": page_title,
            "which_wiki": self.job.which_wiki,

            "refs": page_refs,
        }



