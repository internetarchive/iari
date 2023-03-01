import json
import logging
from os.path import exists
from typing import Optional, Dict, Any

import config
from src import WcdBaseModel
from src.models.api.job import Job
from src.models.exceptions import MissingInformationError

logger = logging.getLogger(__name__)


class FileIo(WcdBaseModel):
    job: Optional[Job] = None
    data: Dict[str, Any] = dict()
    hash: str = ""
    wari_id: str = ""
    subfolder: str = ""

    @property
    def path_filename(self) -> str:
        from src.models.api import app

        path_filename = f"{config.subdirectory_for_json}{self.subfolder}{self.filename}"
        app.logger.debug(f"using path: {path_filename}")
        return path_filename

    @property
    def filename(self) -> str:
        """Returns the filename of the"""
        if not self.hash:
            raise MissingInformationError()
        else:
            return f"{self.hash[:8]}.json"

    def write_to_disk(
        self,
    ) -> None:
        from src.models.api import app

        logger.debug("write_to_disk: running")
        app.logger.debug("write_to_disk: running")
        if self.data:
            path_filename = self.path_filename
            if exists(path_filename):
                with open(file=path_filename, mode="w") as file:
                    logger.debug(f"writing to new file")
                    app.logger.debug(f"writing to new file")
                    # https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file
                    json.dump(self.data, file, ensure_ascii=False, indent=4)
            else:
                # create and write
                with open(file=path_filename, mode="x") as file:
                    logger.debug("overwriting existing file")
                    app.logger.debug("overwriting existing file")
                    # https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file
                    json.dump(self.data, file, ensure_ascii=False, indent=4)
        else:
            app.logger.info("Skipping write because self.data is empty")

    def read_from_disk(self) -> None:
        from src.models.api import app

        message = "read_from_disk: running"
        logger.debug(message)
        app.logger.debug(message)
        path_filename = self.path_filename
        if exists(path_filename):
            with open(file=path_filename) as file:
                # logger.debug("loading json into self.data")
                app.logger.debug("loading json into self.data")
                self.data = json.load(file)
                self.data["served_from_cache"] = True
                # app.logger.debug(f"loaded: {self.statistics_dictionary}")
        else:
            logger.debug("no json on disk")
            app.logger.debug("no json on disk")
