# objhect for wiki article
# pass in analyzer
# - extracts refs?
# Ref Analyzer will just grab refs for this purpose
#     - can reuse ref parsing existing that takes wikitext
# WikiRefAnalyzer - specific analyzer to this task
#
# wiki_page.analyzer.refs ???
#
# wiki_page.refs
# - analyzer sets those
# OR
# append analyzer to wiki_page - ???
#
#
# if not self.page_analyzer:
#     self.page_analyzer = WikipediaAnalyzerV2(job=self.job)
#
# self.io.data = self.page_analyzer.get_article_data()
#
# # if article not found, return error as such
# if not self.page_analyzer.article_found:
#     return AnalyzerReturnValues.NOT_FOUND.value, 404
#
# # if article is a redirect, return error as such
# if self.page_analyzer.is_redirect:
#     app.logger.debug("found redirect")
#     return AnalyzerReturnValues.IS_REDIRECT.value, 400
#
# app.logger.debug("ArticleV2:: processed article, saving...")

from datetime import datetime
from typing import Any, Tuple, Dict, List, Optional
import traceback

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode

from src.models.base import WariBaseModel
from src.models.exceptions import MissingInformationError, WikipediaApiFetchError

from flask_restful import Resource, abort  # type: ignore

from src.models.api.job.article_job import ArticleJob
# from src.models.api.schema.article_schema import ArticleSchema
from src.models.exceptions import MissingInformationError

from src.models.file_io.article_file_io import ArticleFileIo
from src.models.file_io.references import ReferencesFileIo
from src.models.v2.wikimedia.wikipedia.reference.reference_lite_v2 import WikipediaReferenceLiteV2

from src.models.wikimedia.enums import AnalyzerReturnValues, WikimediaDomain
from src.models.wikimedia.wikipedia.analyzer import WikipediaAnalyzer

# from src.views.statistics.write_view import StatisticsWriteView


class WikiArticleV2(WariBaseModel):  ## NB NOT based on StatisticsView or StatisticsWriteView like others
    """
    we really should have a base class of something like "resource with references"
    or something that indicates this is a referencable object

    class for wiki article
    it contains space for references
    An analyzer consumes this article object and extracts references from it
    """

    job: ArticleJob
    wikitext: str
    wikicode: Wikicode = None  # wiki object tree parsed from wikitext

    page_url: str = ""
    page_title: str = ""
    page_lang: str = ""

    references: Optional[List[WikipediaReferenceLiteV2]] = None

    def parse_references(self):
        self.wikicode = mwparserfromhell.parse(self.wikitext)


    def __extract_sections__(self) -> None:
        """This uses the sections regex supplied by the patron via the API
        and populates the sections attribute with a list of MediawikiSection objects

        We only consider level 2 sections beginning with =="""
        from src import app

        self.sections = []
        app.logger.debug("__extract_sections__: running")
        if not self.wikicode:
            self.__parse_wikitext__()

                            # all_sections: List[Wikicode] = self.wikicode.get_sections(
                            #     # levels=[2],
                            #     include_headings=True,
                            # )

                            # section_counter = 0
                            # for section in all_sections:
                            #     section_counter += 1
                            #     app.logger.info(f"All Section #{section_counter}")
                            #
                            #     self.section_list.append({"id": section_counter, "name": "???"})
                            #
                            #     for node in section.filter_headings():
                            #         header_text = node.title.strip()
                            #         header_level = node.level
                            #         # app.logger.info(f"Section id: {section_counter}, Header: {header_text}, Level: {header_level}")
                            #         app.logger.info(f"Section #: {section_counter} header: {node}")

        sections: List[Wikicode] = self.wikicode.get_sections(
            levels=[2],
            include_headings=True,
        )

        '''
        loop thru all sections
        keeping counter
        when level 2 hit, 
            create a mw_section object
            set counter as section_id
        '''

        # TODO: make this code better by special casing no section and making faux section, and putting through same loop

        section_counter = 0
        section_list = []

        if not sections:
            app.logger.debug("No level 2 sections detected, creating root section")
            # console.print(self.wikicode)
            # exit()
            mw_section = MediawikiSection(
                # We add the whole article to the root section
                wikicode=self.wikicode,
                section_id=section_counter,

                job=self.job,

                testing=self.testing,
                language_code=self.language_code,
            )
            mw_section.extract()
            self.sections.append(mw_section)

        else:
            app.logger.info(f"Processing section number {section_counter}")

            # append root section as first section in section list
            self.__extract_root_section__()

            # append each section to section list
            for section in sections:

                section_counter += 1

                app.logger.info(f"Section: {section}")

                mw_section = MediawikiSection(
                    wikicode=section,
                    section_id=section_counter,

                    job=self.job,

                    testing=self.testing,
                    language_code=self.language_code,
                )

                mw_section.extract()  # pull all refs from section
                self.sections.append(mw_section)

                section_list.append({"name": "section name", "counter": section_counter})


        app.logger.debug(f"Number of sections found: {len(self.sections)}")

        self.section_info.update({"count": len(self.sections), "list": section_list})
        # self.section_info["count"] = len(self.sections)
        # self.section_info["list"] = section_list


    # def __handle_article_request__(self):
    #     from src import app
    #
    #     app.logger.info("==> WikiArticleV2::__handle_article_request__: fetching article data and saving to cache")
    #
    #     self.__setup_wikipedia_analyzer__()
    #     return self.__analyze_and_write_and_return__()
    #
    # def __analyze_and_write_and_return__(self) -> Tuple[Any, int]:
    #     """Analyze, calculate the time, write statistics to disk and return it
    #     If we did not get statistics, return a meaningful error to the patron"""
    #     from src import app
    #
    #     app.logger.info("==> __analyze_and_write_and_return__")
    #
    #     if not self.wikipedia_page_analyzer:
    #         raise MissingInformationError("self.wikipedia_page_analyzer was None")
    #
    #     self.__get_statistics__()  # populate self.io.data with analysis results
    #     self.__setup_io__()
    #     self.io.data = self.wikipedia_page_analyzer.get_statistics()
    #
    #     if self.wikipedia_page_analyzer.found:  # found === True means article was successfully processed
    #         app.logger.debug("valid article found and processed")
    #
    #         if self.wikipedia_page_analyzer.is_redirect:
    #             app.logger.debug("found redirect")
    #             return AnalyzerReturnValues.IS_REDIRECT.value, 400
    #
    #         else:
    #             app.logger.debug("adding time information and returning the statistics")
    #             self.__update_statistics_with_time_information__()
    #             # we got a json response
    #             # according to https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view
    #             # flask calls jsonify automatically
    #             self.__write_to_disk__()  # writes self.io.dtata to disk
    #             if not self.io:
    #                 raise MissingInformationError()
    #             if self.io.data:
    #                 self.io.data["served_from_cache"] = False  # append return data
    #                 return self.io.data, 200
    #             else:
    #                 raise MissingInformationError()
    #     else:
    #         return AnalyzerReturnValues.NOT_FOUND.value, 404
    #
    # def __get_statistics__(self):
    #     """
    #     get the results from wikipedia_page_analyzer.get_statistics and save to self.io.data
    #     """
    #     from src import app
    #
    #     app.logger.debug("==> __get_statistics__")
    #
    #     if not self.wikipedia_page_analyzer:
    #         raise MissingInformationError("self.wikipedia_page_analyzer was None")
    #
    #     # https://realpython.com/python-timer/
    #     self.__setup_io__()
    #     self.io.data = self.wikipedia_page_analyzer.get_statistics()
    #
    # def __update_statistics_with_time_information__(self):
    #     """Update the dictionary before returning it"""
    #     if self.io.data:
    #         timestamp = datetime.timestamp(datetime.utcnow())
    #         self.io.data["timestamp"] = int(timestamp)
    #         isodate = datetime.isoformat(datetime.utcnow())
    #         self.io.data["isodate"] = str(isodate)
    #     else:
    #         raise ValueError("not a dict")
    #
    # def __return_meaningful_error__(self):
    #     from src import app
    #
    #     app.logger.error("==> __return_meaningful_error__")
    #     if self.job.title == "":
    #         return "Title was missing", 400
    #     if self.job.domain != "wikipedia":
    #         return "Only 'wikipedia' site is supported", 400
    #
    # def __setup_wikipedia_analyzer__(self):
    #     if not self.wikipedia_page_analyzer:
    #         from src import app
    #
    #         app.logger.info(f"Setup analyzer for {self.job.title}...")
    #
    #         # wikipedia_page_analyzer is declared in the StatisticsView class (views/statistics/__init.py)
    #         # NB This wrong! It should be declared here in the Article class.
    #         #   we fix this in the v2/ArticleV2 code, but not here, since it "works".
    #         #   this is the only place it is called, so it makes no sense to
    #         #   declare it in a base class that other objects that do not use
    #         #   the analysis feature...!
    #         self.wikipedia_page_analyzer = WikipediaAnalyzer(job=self.job)
    #
    # def __setup_io__(self):
    #     self.io = ArticleFileIo(job=self.job)
    #
    # def __write_to_disk__(self):
    #     """Write both article json and all reference json files"""
    #     from src import app
    #
    #     app.logger.debug("__write_to_disk__: running")
    #     if not self.job.testing:
    #         self.__write_article_to_disk__()
    #         self.__write_references_to_disk__()
    #
    # def __write_article_to_disk__(self):
    #     article_io = ArticleFileIo(
    #         job=self.job,
    #         data=self.io.data,
    #         wari_id=self.job.wari_id,
    #     )
    #     article_io.write_to_disk()
    #
    # def __write_references_to_disk__(self):
    #     references_file_io = ReferencesFileIo(
    #         references=self.wikipedia_page_analyzer.reference_statistics
    #     )
    #     references_file_io.write_references_to_disk()
