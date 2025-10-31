import logging
from typing import Any, Dict, Optional

from src.models.file_io.hash_based import HashBasedFileIo

logger = logging.getLogger(__name__)


class XhtmlFileIo(HashBasedFileIo):
    data: Optional[Dict[str, Any]] = None
    subfolder: str = "xhtmls/"
