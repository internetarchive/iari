import logging

# from os.path import exists
from typing import Any, Optional

from pydantic import BaseModel, validate_arguments

logger = logging.getLogger(__name__)


class IariBaseModel(BaseModel):
    """Iari base model has any methods that we may need
    in more than one class"""

    # We set to Any here because of cyclic dependency or pydantic forward ref error
    cache: Optional[Any] = None

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
        # WTF: what is this and where is it used?

    # @validate_arguments
    # # NB: this is a pydantic thing.
    # #   from what i understand, it validates the parameters to __log_to_file__,
    # #   which, as far as i can tell, is not used and commented out everywhere.
    # def __log_to_file__(self, message: str, file_name: str) -> None:
    #     if not exists(file_name):
    #         logger.debug(f"Creating {file_name}")
    #         with open(file_name, "x"):
    #             pass
    #     with open(file_name, "a") as f:
    #         logger.debug(f"Writing entry to {file_name}")
    #         f.write(f"{message}\n")
