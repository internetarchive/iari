# from flask_restful import Resource, abort  # type: ignore
# from marshmallow import Schema
from datetime import datetime
from typing import Any, Optional, Tuple
import traceback

from dateutil.parser import isoparse

import config
import requests

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError

from src.models.v2.schema.editref_schema_v2 import EditRefSchemaV2
from src.models.v2.job.editref_job_v2 import EditRefJobV2

# from src.models.v2.file_io.article_file_io_v2 import ArticleFileIoV2
# from src.models.v2.wikimedia.wikipedia.analyzer_v2 import WikipediaAnalyzerV2
# from src.models.wikimedia.enums import AnalyzerReturnValues, WikimediaDomain
from src.views.v2.statistics import StatisticsViewV2


from src.helpers.get_version import get_poetry_version


class EditRefV2(StatisticsViewV2):
    # TODO Since no setup_io is needed for this endpoint, we could maybe
    #   base this on an "Execution" view? or a generic "Action" view?

    """
    replaces search string with replace string in source string, and returns results
    """

    schema = EditRefSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: EditRefJobV2           # Holds usable variables, seeded from schema. Overrides StatisticsViewV2's "job"

    source_text = ""
    replaced_data = ""

    def get(self):
        """
        flask GET entrypoint for returning editref results
        must return a tuple: (Any,response_code)
        """
        from src import app
        app.logger.debug("==> EditRefV2::get")

        return self.__process_data__(method="get")

    def post(self):
        """
        flask POST entrypoint for returning editref results
        must return a tuple: (Any,response_code)
        """
        from src import app
        app.logger.debug("==> EditRefV2::post")

        return self.__process_data__(method="post")


    def __process_data__(self, method="get"):
        from src import app
        try:
            self.__validate_and_get_job__(method)  # inherited from StatisticsViewV2
            #
            # validates schema params (a marshmallow feature), and sets job properties based on schema's values
            """
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
            """
            # set up source_text
            self.__setup_source_text__()  # setup source_text to be

            # set up results
            self.__replace_data__()  # self.replaced_data holds newly edited source

            # and return results
            # return {
            #     "old_ref": self.job.old_ref,
            #     "new_ref": self.job.new_ref,
            #     # "source": self.job.source,
            #     "result": self.replaced_data
            # }
            return self.replaced_data


        except MissingInformationError as e:
            app.logger.debug("after EditRefV2::self.__validate_and_get_job__ MissingInformationError exception")
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            app.logger.debug("after EditRefV2::self.__validate_and_get_job__ exception")
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500

    def __setup_source_text__(self):
        from src import app
        app.logger.debug("==> EditRefV2::__setup_source_text__")

        """
        set source_text to:
            job.source if non-empty
            fetched wikitext based on wiki_page_url otherwise
                - EXCEPTION No Wiki Page
                - EXCEPTION General
        """
        if self.job.source:
            self.source_text = self.job.source

        else:
            # grab wikitext from wiki_page_url

            url = (
                f"https://{self.job.wiki_lang}.{self.job.wiki_domain.value}/"
                f"w/rest.php/v1/page/{self.job.quoted_title}"
            )
            headers = {"User-Agent": config.user_agent}
            response = requests.get(url, headers=headers)

            # console.print(response.json())
            app.logger.debug(f"==> EditRefV2::__setup_source_text__: url to grab is: {url}")

            if response.status_code == 200:

                data = response.json()

                self.job.wiki_revision = int(data["latest"]["id"])
                self.revision_isodate = isoparse(data["latest"]["timestamp"])
                self.revision_timestamp = round(self.revision_isodate.timestamp())
                self.page_id = int(data["id"])

                self.source_text = data["source"]

            else:
                # raise an exception because wiki page fetch was unsuccessful
                app.logger.error(f"==> EditRefV2::__setup_source_text__: wikitext fetch was unsuccessful "
                                 f"({self.job.wiki_page_url})")

    def __replace_data__(self):
        # takes source_text and applies replacement transformations on it
        from src import app
        app.logger.debug("==> EditRefV2::__replace_data__")

        app.logger.debug("==>")
        app.logger.debug("==>")
        app.logger.debug("==>")

        app.logger.debug("==>")
        app.logger.debug("==> SOURCE")
        app.logger.debug("==>")
        app.logger.debug(self.source_text)

        self.replaced_data = self.source_text.replace(self.job.old_ref, self.job.new_ref)

        app.logger.debug("==>")
        app.logger.debug("==> REPLACED")
        app.logger.debug("==>")
        app.logger.debug(self.replaced_data)


