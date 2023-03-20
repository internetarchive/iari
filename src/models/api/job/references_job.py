from src.models.api.job import Job


class ReferencesJob(Job):
    wari_id: str = ""
    all: bool = False
    chunk_size: int = 10
    offset: int = 0
