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
    data: Optional[Dict[str, Any]] = None
    wari_id: str = ""
    subfolder: str = ""
    iari_prefix: str = ""
    testing: bool = False

    @property
    def filename(self):
        from src import app

        app.logger.debug(f"FileIo: filename: iari_prefix = {self.iari_prefix}")
        app.logger.debug(
            f"FileIo: filename: filename could be {self.iari_prefix}{self.wari_id}"
        )

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

        # app.logger.debug(f"FileIo:: using path: {path_filename} (subfolder: {self.subfolder})")
        app.logger.debug(f"FileIo: [path_filename] iari_prefix = {self.iari_prefix}")
        return path_filename

    def write_to_disk(
        self,
    ) -> None:

        from src import app

        # app.logger.debug(os.getcwd())

        if self.data:
            path_filename = self.path_filename

            app.logger.debug(f"FileIo::write_to_disk: path_filename: {path_filename}")
            app.logger.debug(f"FileIo::write_to_disk: iari_prefix: {self.iari_prefix}")

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

        path_filename = self.path_filename

        app.logger.debug(f"FileIo::read_from_disk: path_filename: {path_filename}")
        app.logger.debug(f"FileIo::read_from_disk: iari_prefix: {self.iari_prefix}")

        if exists(path_filename):
            with open(file=path_filename) as file:
                # logger.debug("loading json into self.data")
                app.logger.debug("loading json into self.data")
                # self.data = {}
                self.data = json.load(file)
                if self.data:
                    self.data["served_from_cache"] = True
                # app.logger.debug(f"loaded: {self.statistics_dictionary}")
        else:
            logger.debug("no json on disk")
