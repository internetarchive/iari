from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo


class HashBasedFileIo(FileIo):
    hash_based_id: str
    prefix = ""
    iari_prefix_for_hash = "IPFH"

    @property
    def filename(self) -> str:
        """Returns the filename of the"""
        from src import app

        app.logger.debug(f"HashBasedFileIo:[filename] prefix = {self.prefix}")
        app.logger.debug(
            f"HashBasedFileIo:[filename] iari_prefix_for_hash = {self.iari_prefix_for_hash}"
        )

        if not self.hash_based_id:
            raise MissingInformationError("no hash based id")
        else:
            return f"{self.hash_based_id}.json"
