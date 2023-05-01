import json
import logging
from os.path import exists
from typing import Any, Dict, Optional

import config
from src.models.api.job import Job
from src.models.base import WariBaseModel

logger = logging.getLogger(__name__)


class FileIo(WariBaseModel):
    job: Optional[Job] = None
    data: Dict[str, Any] = {}
    wari_id: str = ""
    subfolder: str = ""
    testing: bool = False

    @property
    def filename(self):
        return f"{self.wari_id}.json"

    @property
    def path_filename(self) -> str:
        from src import app

        if self.testing:
            # go out to repo root first
            # print(os.getcwd())
            # we hard code the json directory for now
            path_filename = f"/home/dpriskorn/src/python/wcdimportbot/{config.subdirectory_for_json}{self.subfolder}{self.filename}"
        else:
            path_filename = (
                f"{config.subdirectory_for_json}{self.subfolder}{self.filename}"
            )
        app.logger.debug(f"using path: {path_filename}")
        return path_filename

    def write_to_disk(
        self,
    ) -> None:
        from src import app

        app.logger.debug("write_to_disk: running")
        # app.logger.debug(os.getcwd())
        if self.data:
            path_filename = self.path_filename
            if exists(path_filename):
                with open(file=path_filename, mode="w") as file:
                    app.logger.debug("overwriting existing file")
                    # https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file
                    json.dump(self.data, file, ensure_ascii=False, indent=4)
            else:
                # x = create and write
                with open(file=path_filename, mode="x") as file:
                    app.logger.debug("writing to new file")
                    # https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file
                    json.dump(self.data, file, ensure_ascii=False, indent=4)
        else:
            app.logger.info("Skipping write because self.data is empty")

    def read_from_disk(self) -> None:
        from src import app

        message = "read_from_disk: running"
        app.logger.debug(message)
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
