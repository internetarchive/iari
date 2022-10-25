from datetime import datetime

from src import WcdBaseModel


class Meta(WcdBaseModel):
    id: str
    dt: datetime
    domain: str
    offset: int
