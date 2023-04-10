from typing import Optional

from src.models.api.job import Job
from src.models.base import WariBaseModel


class JobBaseModel(WariBaseModel):
    job: Optional[Job] = None

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
