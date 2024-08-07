from typing import Any, Dict, List, Optional

from src.helpers.console import console
from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo
from src.models.v2.file_io.reference_file_io_v2 import ReferenceFileIoV2


class ReferencesFileIoV2(FileIo):
    references: Optional[List[Dict[str, Any]]] = None

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
            reference_io = ReferenceFileIoV2(
                job=self.job, hash_based_id=reference["id"], data=reference
            )
            reference_io.write_to_disk()
        if self.references:
            app.logger.debug(f"wrote {len(self.references)} references to disk")
        else:
            app.logger.debug("wrote 0 references to disk")
