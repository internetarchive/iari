import logging
from typing import Any, Dict

from src.models.file_io.hash_based import HashBasedFileIo

logger = logging.getLogger(__name__)


class XhtmlFileIo(HashBasedFileIo):
    data: Dict[str, Any] = dict()
    subfolder = "xhtmls/"
