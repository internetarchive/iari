import logging
from typing import Any, Dict

from src.models.file_io import FileIo

logger = logging.getLogger(__name__)


class UrlFileIo(FileIo):
    data: Dict[str, Any] = dict()
    subfolder = "urls/"
