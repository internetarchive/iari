from src.v3.models.exceptions import MissingInformationError
from src.v3.models.file_io import FileIo


class HashBasedFileIo(FileIo):
    hash_based_id: str

    @property
    def filename(self) -> str:
        """Returns the filename of the"""
        if not self.hash_based_id:
            raise MissingInformationError("no hash based id")
        else:
            return f"{self.hash_based_id}.json"
