from pydantic import BaseModel


class CheckUrlJob(BaseModel):
    url: str
    timeout: int = 2  # We default to 2 seconds
