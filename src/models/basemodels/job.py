from typing import Optional

from src.models.api.job import Job
from src.wcd_base_model import WcdBaseModel


class JobBaseModel(WcdBaseModel):
    job: Optional[Job] = None
