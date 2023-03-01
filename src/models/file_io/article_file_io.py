import logging
from typing import Any, Dict

from src.models.file_io import FileIo

logger = logging.getLogger(__name__)


class ArticleFileIo(FileIo):
    data: Dict[str, Any] = dict()
    subfolder = "articles/"

    @property
    def filename(self) -> str:
        filename = f"{self.wari_id}.json"
        return filename
