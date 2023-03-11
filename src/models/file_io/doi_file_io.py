import logging
from typing import Any, Dict

from src.models.file_io import FileIo

logger = logging.getLogger(__name__)


class DoiFileIo(FileIo):
    data: Dict[str, Any] = dict()
    subfolder = "dois/"