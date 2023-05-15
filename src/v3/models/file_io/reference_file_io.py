import logging
from typing import Any, Dict

from src.v3.models.file_io.hash_based import HashBasedFileIo

logger = logging.getLogger(__name__)


class ReferenceFileIo(HashBasedFileIo):
    data: Dict[str, Any] = dict()
    subfolder = "references/"
