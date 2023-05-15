from typing import Optional

from src.v3.models.api.job import Job
from src.v3.models.base import WariBaseModel


class JobBaseModel(WariBaseModel):
    job: Optional[Job] = None

    class Config:  # dead: disable
        extra = "forbid"  # dead: disable
