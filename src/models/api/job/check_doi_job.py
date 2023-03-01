from pydantic import BaseModel


class CheckDoiJob(BaseModel):
    doi: str
