from pydantic import BaseModel


class JobV2(BaseModel):
    refresh: bool = False
    testing: bool = False
