import logging
from os.path import exists
from typing import Any, Optional

from pydantic import BaseModel, validate_arguments

logger = logging.getLogger(__name__)


class WariBaseModel(BaseModel):
    """This base model has all methods that we
    want to use in more than one class"""

    # We set to Any here because of cyclic dependency or pydantic forward ref error
    cache: Optional[Any] = None

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable

    @validate_arguments
    def __log_to_file__(self, message: str, file_name: str) -> None:
        if not exists(file_name):
            logger.debug(f"Creating {file_name}")
            with open(file_name, "x"):
                pass
        with open(file_name, "a") as f:
            logger.debug(f"Writing entry to {file_name}")
            f.write(f"{message}\n")
