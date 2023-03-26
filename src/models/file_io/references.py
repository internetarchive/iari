from typing import List, Any, Dict

from src import console
from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo
from src.models.file_io.reference_file_io import ReferenceFileIo


class ReferencesFileIo(FileIo):
    data: List[Dict[str, Any]] = []
    def write_references_to_disk(self):
        from src.models.api import app

        app.logger.debug("writing references to disk")
        for reference in self.data:
            # this is a dict
            if "id" not in reference:
                console.print(reference)
                raise MissingInformationError("no id found in reference")
            # if "wikitext" in reference:
            app.logger.debug(reference)
            exit()
            reference_io = ReferenceFileIo(
                job=self.job, hash_based_id=reference["id"], data=reference
            )
            reference_io.write_to_disk()
        app.logger.debug(
            f"wrote {len(self.data)} "
            f"references to disk"
        )
