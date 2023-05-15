from typing import Any, Dict, List

from src.v3.helpers.console import console
from src.v3.models.exceptions import MissingInformationError
from src.v3.models.file_io import FileIo
from src.v3.models.file_io.reference_file_io import ReferenceFileIo


class ReferencesFileIo(FileIo):
    references: List[Dict[str, Any]] = []

    def write_references_to_disk(self):
        from src import app

        app.logger.debug("writing references to disk")
        for reference in self.references:
            # this is a dict
            if "id" not in reference:
                console.print(reference)
                raise MissingInformationError("no id found in reference")
            if not reference["id"]:
                console.print(reference)
                raise MissingInformationError("empty id found in reference")
            # if "wikitext" in reference:
            # app.logger.debug(reference)
            reference_io = ReferenceFileIo(
                job=self.job, hash_based_id=reference["id"], data=reference
            )
            reference_io.write_to_disk()
        app.logger.debug(f"wrote {len(self.data)} references to disk")
