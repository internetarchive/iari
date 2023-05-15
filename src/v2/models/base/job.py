from typing import Optional

from src.v2.models.api.job import Job
from src.v2.models.base import WariBaseModel


class JobBaseModel(WariBaseModel):
    job: Optional[Job] = None

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
