from pydantic import BaseModel


class Job(BaseModel):
    user_agent = "IARI, see https://github.com/internetarchive/iari"
    refresh: bool = False
    testing: bool = False
