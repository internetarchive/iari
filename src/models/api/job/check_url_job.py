from src.models.api.job import Job


class CheckUrlJob(Job):
    url: str
    timeout: int = 2  # We default to 2 seconds
