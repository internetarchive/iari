from pydantic import BaseModel


class LinksAggregates(BaseModel):
    all: int = 0
    s200: int = 0
    s3xx: int = 0
    s404: int = 0
    s5xx: int = 0
    error: int = 0
    no_dns: int = 0
    other_2xx: int = 0
    other_4xx: int = 0
