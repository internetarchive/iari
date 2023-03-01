import json
import logging
from os.path import exists
from typing import Any, Dict

import config
from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo

logger = logging.getLogger(__name__)


class ReferenceFileIo(FileIo):
    data: Dict[str, Any] = dict()
    subfolder = "references/"

