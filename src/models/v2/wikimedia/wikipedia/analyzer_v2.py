import logging
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models.exceptions import MissingInformationError

# from src.models.base import WariBaseModel
from src.models.v2.base import IariBaseModel
from src.models.v2.job.article_job_v2 import ArticleJobV2
from src.models.v2.statistics.article_stats_v2 import ArticleStatisticsV2
from src.models.v2.statistics.reference_stats_v2 import ReferenceStatisticsV2
from src.models.v2.wikimedia.wikipedia.article_v2 import WikipediaArticleV2
from src.models.wikimedia.wikipedia.reference.enums import (
    FootnoteSubtype,
    ReferenceType,
)

logger = logging.getLogger(__name__)


class WikipediaAnalyzerV2(IariBaseModel):
    """contains logic for getting the article and reference statistics
    and mapping them to the API output model

    It does not handle storing on disk.
    """

    job: Optional[ArticleJobV2] = None
    article: Optional[WikipediaArticleV2] = None

    article_statistics: Optional[ArticleStatisticsV2] = None
    reference_statistics: Optional[List[Dict[str, Any]]] = None

    @property
    def testing(self):
        if not self.job:
            raise MissingInformationError("no job")
        return self.job.testing

    @property
    def is_redirect(self) -> bool:
        if not self.article:
            raise MissingInformationError("self.article was None")
        return self.article.is_redirect

    @property
    def article_found(self) -> bool:
        if not self.article:
            raise MissingInformationError("self.article was None")
        return self.article.found_in_wikipedia

    # returns dict of article data ( self.article_statistics.dict() )
    def get_article_data(self) -> Dict[str, Any]:

        # NB WTF TODO the goal: return self.article_statistics.dict()

        self.__get_article_object__()  # sets self.article

        if self.article:
            self.article.fetch_and_parse()
            # WikipediaArticleV2 (article_v2):
            # fetches wikitext (we need to fetch html)
            # skips if redirect
            # errors if page not found
            # sets self.extractor
            # self.extractor.extract_all_references  # WikipediaReferenceExtractorV2
            #   this is what does the wikitext and html parsing (we willbe doing html parsing)
            #   so, what we need is:
            #       1. get html contents of file (see __fetch_wikitext__ in article_v2)
            #       2. parse into properties of self

            # what this did was set extract.references, i think...

        if not self.article_statistics:  # which is probably not yet true
            # because we haven't extracted yet...

            # populate self.article_statistics (if successful)
            self.__gather_article_statistics__()  # local class function

            # # populate self.reference_statistics
            # self.__gather_reference_statistics__()

            # # insert references into article stats
            # if self.article_statistics:
            #     self.article_statistics.references = self.reference_statistics

        # return dict of data
        if self.article_statistics:
            return self.article_statistics.dict()
        else:
            return {}

        # def __analyze__(self):
        #     """Helper method"""
        #     from src import app
        #     app.logger.debug("WikipediaAnalyzerV2::__analyze__")
        #     if self.job:
        #         if not self.article:
        #             self.__populate_article__()
        #         if self.article:
        #             self.article.fetch_and_extract_and_parse()

    def __get_article_object__(self):
        """
        fills the article object
        """
        if not self.job:
            raise MissingInformationError()

        if not self.article:
            # self.__analyze__()
            # self.__assign_article__()
            if self.job and self.job.title:
                # Todo consider propagating job further here
                # WTF ^^^ what does that mean??? ^^^
                self.article = WikipediaArticleV2(
                    job=self.job,
                )
            else:
                raise MissingInformationError("Missing Job title")

    def __gather_article_statistics__(self) -> None:
        """
        sets self.article_statistics with gathered data from article
        """
        if not (
            self.job
            and self.article
            and not self.article.is_redirect
            and self.article.found_in_wikipedia
        ):
            pass  # do nothing ... cannot continue if these conditions are not met

        # abort with error if the following conditions are not met either

        # if not self.article.extractor:
        #     raise MissingInformationError("self.article.extractor is None")

        if not self.article.revision_id:
            raise MissingInformationError("self.article.revision_id is None")

        if not self.article.revision_isodate:
            raise MissingInformationError("self.article.revision_isodate is None")

        if not self.article.revision_timestamp:
            raise MissingInformationError("self.article.revision_timestamp is None")

        # ae = self.article.extractor

        if not self.job.page_id:
            self.job.get_mediawiki_ids()

        self.article_statistics = ArticleStatisticsV2(
            new_iari_article_data=True,
            new_data={"new_data": "new data here"},
            new_references=self.article.references,
            iari_id=self.job.iari_id,
            lang=self.job.lang,
            site=self.job.domain.value,
            title=self.job.title,
            page_id=self.article.page_id,
            revision_id=self.article.revision_id,
            revision_isodate=self.article.revision_isodate.isoformat(),
            revision_timestamp=self.article.revision_timestamp,
            served_from_cache=False,
            isodate=datetime.utcnow().isoformat(),
            # ores_score=self.article.ores_details,
            # reference_statistics={
            #     "named": ae.number_of_empty_named_references,
            #     "footnote": ae.number_of_footnote_references,
            #     "content": ae.number_of_content_references,
            #     "general": ae.number_of_general_references,
            # },
            # urls=ae.raw_urls,
            # fld_counts=ae.first_level_domain_counts,
            # cite_refs=ae.cite_refs,
            # cite_refs_count=ae.cite_refs_count,
        )

    #
    # def __assign_article__(self):
    #
    #     from src import app
    #     app.logger.debug("WikipediaAnalyzerV2::__populate_article__")
    #
    #     if self.job and self.job.title:
    #         # Todo consider propagating job further here
    #         # WTF what does that mean???
    #         self.article = WikipediaArticleV2(
    #             job=self.job,
    #         )
    #     else:
    #         raise MissingInformationError("Missing Job title")

    # def __get_statistics_dict__(self) -> Dict[str, Any]:
    #     if self.article_statistics:
    #         return self.article_statistics.dict()
    #     else:
    #         return {}

    # def __gather_reference_statistics__(self):
    #     from src import app
    #
    #     self.reference_statistics = []
    #     app.logger.debug("__gather_reference_statistics__: running")
    #
    #     if (
    #             self.article
    #             and self.article.extractor
    #             and self.article.extractor.references
    #     ):
    #         app.logger.debug(
    #             f"Gathering reference statistics for "
    #             f"{self.article.extractor.number_of_references} references"
    #         )
    #
    #         # app.logger.debug(f"### ### ###")
    #         # app.logger.debug(f"### START ###")
    #         # app.logger.debug(f"__gather_reference_statistics__")
    #         # app.logger.debug(f"### ### ###")
    #         # app.logger.debug(f"### ### ###")
    #
    #         ref_counter = 0
    #
    #         for reference in self.article.extractor.references:
    #             if not reference:
    #                 raise MissingInformationError("raw_reference was None")
    #             subtype = (
    #                 reference.footnote_subtype.value
    #                 if reference.footnote_subtype
    #                 else ""
    #             )
    #
    #             # TODO REMOVE
    #             app.logger.debug(
    #                 f"type, subtype: {reference.reference_type.value}:{subtype}"
    #             )
    #
    #             # an attempt to get positional index of citation to match those of returned HTML
    #             # only add ref_index if we are a CONTENT footnote and not NAMED
    #             ref_index = 0
    #             if (
    #                     reference.reference_type.value == ReferenceType.FOOTNOTE.value
    #                     and subtype == FootnoteSubtype.CONTENT.value
    #             ):
    #                 ref_counter += 1
    #                 ref_index = ref_counter
    #
    #             # if not rr.get_wikicode_as_string:
    #             #     raise MissingInformationError()
    #
    #             data = ReferenceStatisticsV2(
    #                 id=reference.reference_id,
    #                 name=reference.get_name,
    #                 type=reference.reference_type.value,
    #                 footnote_subtype=subtype,
    #                 ref_index=ref_index,
    #                 titles=reference.titles,
    #                 flds=reference.unique_first_level_domains
    #                 if reference.unique_first_level_domains
    #                 else [],
    #                 wikitext=reference.get_wikicode_as_string,
    #                 section=reference.section,
    #                 template_names=reference.template_names,
    #                 templates=reference.get_template_dicts,
    #                 urls=reference.raw_urls,
    #                 url_objects=reference.get_reference_url_dicts,
    #             ).dict()
    #             self.reference_statistics.append(data)
    #
    #         # app.logger.debug(f"### ### ###")
    #         # app.logger.debug(f"### END ###")
    #         # app.logger.debug(f"### ### ###")
    #
    #     if not self.article_statistics:
    #         app.logger.debug(
    #             "self.article_statistics was None "
    #             "so we skip gathering reference statistics"
    #         )

    # def __extract_dehydrated_references__(self):
    #     # We use a local variable here to avoid this regression
    #     # https://github.com/internetarchive/wari/issues/700
    #     self.dehydrated_reference_statistics = deepcopy(self.reference_statistics)
    #     for data in self.dehydrated_reference_statistics:
    #         # We return most of the data including the wikitext to accommodate
    #         # see https://github.com/internetarchive/iari/issues/831
    #         del data["templates"]
    #         del data["url_objects"]
    #
    # def __insert_dehydrated_references_into_the_article_statistics__(self):
    #     if self.article_statistics:
    #         self.article_statistics.dehydrated_references = (
    #             self.dehydrated_reference_statistics
    #         )

    # def __insert_references_into_article_stats__(self):
    #     """We return the full reference to accommodate IARE, see https://github.com/internetarchive/iari/issues/886"""
    #     if self.article_statistics:
    #         self.article_statistics.references = self.reference_statistics
