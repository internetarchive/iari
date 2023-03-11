from src.models.api.job import Job


class CheckDoiJob(Job):
    doi: str
    timeout: int = 2
