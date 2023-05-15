from pydantic import BaseModel


class Job(BaseModel):
    refresh: bool = False
    testing: bool = False
