import logging
import re
from typing import List, Optional, Union

import mwparserfromhell  # type: ignore
from mwparserfromhell.wikicode import Wikicode  # type: ignore
from pydantic import BaseModel

from src.models.api.job.article_job import ArticleJob
from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference

logger = logging.getLogger(__name__)


class MediawikiSection(BaseModel):
    """This accepts both wikicode directly from mwparserfromhell and wikitext"""

    testing: bool = False
    language_code: str = ""
    wikicode: Optional[Wikicode] = None
    wikitext: str = ""
    references: List[WikipediaReference] = []
    job: ArticleJob

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    @property
    def is_general_reference_section(self):
        if not self.job.regex:
            raise MissingInformationError("No regex in job")
        return bool(re.findall(pattern=self.job.regex, flags=re.I, string=self.name))

    @property
    def __get_lines__(self):
        if not self.wikitext:
            self.__populate_wikitext__()
        return self.wikitext.split("\n")

    @property
    def name(self) -> str:
        """Extracts a section name from the first line of the output from mwparserfromhell"""
        line = self.__get_lines__[0]
        # Handle special case where no level 2 heading is at the beginning of the section
        if "==" not in line:
            logger.info(f"== not found in line {line}")
            return "root"
        else:
            return str(self.__extract_name_from_line__(line=line))

    @property
    def number_of_references(self):
        return len(self.references)

    @staticmethod
    def star_found_at_line_start(line) -> bool:
        """This determines if the line in the current section has a star"""
        return bool("*" in line[:1])

    def __extract_name_from_line__(self, line):
        from src import app

        app.logger.debug("extract_name_from_line: running")
        return line.replace("=", "")

    def __extract_all_general_references__(self):
        from src import app

        app.logger.debug("__extract_all_general_references__: running")
        if self.is_general_reference_section:
            app.logger.info("Regex match on section name")
            # Discard the header line
            lines = self.wikitext.split("\n")
            lines_without_heading = lines[1:]
            logger.debug(
                f"Extracting {len(lines_without_heading)} lines form section {lines[0]}"
            )
            for line in lines_without_heading:
                logger.info(f"Working on line: {line}")
                # Guard against empty line
                # logger.debug("Parsing line")
                # We discard all lines not starting with a star to avoid all
                # categories and other templates not containing any references
                if line and self.star_found_at_line_start(line=line):
                    parsed_line = mwparserfromhell.parse(line)
                    logger.debug("Appending line with star to references")
                    # We don't know what the line contains besides a start
                    # but we assume it is a reference
                    reference = WikipediaReference(
                        wikicode=parsed_line,
                        # wikibase=self.wikibase,
                        testing=self.testing,
                        language_code=self.language_code,
                        is_general_reference=True,
                        section=self.name,
                    )
                    reference.extract_and_check()
                    self.references.append(reference)

    def __extract_all_footnote_references__(self):
        """This extracts everything inside <ref></ref> tags and needs self.wikicode"""
        from src import app

        app.logger.debug("__extract_all_footnote_references__: running")
        # Thanks to https://github.com/JJMC89,
        # see https://github.com/earwig/mwparserfromhell/discussions/295#discussioncomment-4392452
        if not self.wikicode:
            raise MissingInformationError(
                f"The section {self} did not have any wikicode"
            )
        refs = self.wikicode.filter_tags(matches=lambda tag: tag.tag.lower() == "ref")
        app.logger.debug(f"Number of refs found: {len(refs)}")
        for ref in refs:
            reference = WikipediaReference(
                wikicode=ref,
                # wikibase=self.wikibase,
                testing=self.testing,
                language_code=self.language_code,
                section=self.name,
            )
            reference.extract_and_check()
            self.references.append(reference)

    def extract(self):
        if not self.wikicode and not self.wikitext:
            raise MissingInformationError(
                "We need either wikicode or wikitext to continue"
            )
        self.__populate_wikitext__()
        self.__parse_wikitext__()
        self.__extract_all_general_references__()
        self.__extract_all_footnote_references__()

    def __populate_wikitext__(self):
        from src import app

        app.logger.debug("__populate_wikitext__: running")
        if self.wikicode and not self.wikitext:
            self.wikitext = str(self.wikicode)

    def __parse_wikitext__(self):
        from src import app

        app.logger.debug("__parse_wikitext__: running")
        if self.wikitext and not self.wikicode:
            self.wikicode = mwparserfromhell.parse(self.wikitext)
