from datetime import datetime

from src.wcd_base_model import WcdBaseModel


class Meta(WcdBaseModel):
    id: str
    dt: datetime
    domain: str
    offset: int
