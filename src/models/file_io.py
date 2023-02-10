import json
import logging
from os.path import exists
from typing import Any, Dict, Optional

import config
from src import WcdBaseModel
from src.models.api.job import Job
from src.models.exceptions import MissingInformationError

logger = logging.getLogger(__name__)


class FileIo(WcdBaseModel):
    job: Optional[Job] = None
    statistics_dictionary: Dict[str, Any] = dict()

    def write_to_disk(
        self,
    ) -> None:
        from src.models.api import app

        logger.debug("write_to_disk: running")
        app.logger.debug("write_to_disk: running")
        if self.statistics_dictionary:
            page_id = self.statistics_dictionary.get("page_id")
            if not page_id:
                raise MissingInformationError(
                    "no page_id in self.statistics_dictionary"
                )
            filename = self.filename(page_id=int(page_id))
            if exists(filename):
                with open(file=filename, mode="w") as file:
                    logger.debug(f"writing to new file")
                    app.logger.debug(f"writing to new file")
                    # https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file
                    json.dump(
                        self.statistics_dictionary, file, ensure_ascii=False, indent=4
                    )
            else:
                # create and write
                with open(file=filename, mode="x") as file:
                    logger.debug("overwriting existing file")
                    app.logger.debug("overwriting existing file")
                    # https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file
                    json.dump(
                        self.statistics_dictionary, file, ensure_ascii=False, indent=4
                    )
        else:
            app.logger.info(
                "Skipping write because self.statistics_dictionary is empty"
            )

    def read_from_disk(self) -> None:
        from src.models.api import app

        message = "read_from_disk: running"
        logger.debug(message)
        app.logger.debug(message)
        if not self.job:
            raise MissingInformationError("no job")
        if not self.job.page_id:
            self.job.get_page_id()
        filename = self.filename(page_id=self.job.page_id)
        if exists(filename):
            with open(file=filename) as file:
                logger.debug("loading json into self.get_statistics")
                app.logger.debug("loading json into self.get_statistics")
                self.statistics_dictionary = json.load(file)
                self.statistics_dictionary["served_from_cache"] = True
                # app.logger.debug(f"loaded: {self.statistics_dictionary}")
        else:
            logger.debug("no json on disk")
            app.logger.debug("no json on disk")

    def filename(self, page_id: int = 0) -> str:
        from src.models.api import app

        if not self.job:
            raise MissingInformationError("self.job was None")
        filename = f"{config.subdirectory_for_json}{self.job.lang.value}.{self.job.site.value}.org:{page_id}"
        logger.debug(f"using filename: {filename}")
        app.logger.debug(f"using filename: {filename}")
        return filename
