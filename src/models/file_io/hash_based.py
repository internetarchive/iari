from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo


class HashBasedFileIo(FileIo):
    hash_based_id: str
    file_prefix: str = ""

    @property
    def filename(self) -> str:
        """Returns the filename consisting of hash based id and optional prefix"""

        file_prefix = self.file_prefix
        if file_prefix != "":
            file_prefix = file_prefix + "-"

        if not self.hash_based_id:
            raise MissingInformationError("no hash based id")
        else:
            return f"{file_prefix}{self.hash_based_id}.json"
