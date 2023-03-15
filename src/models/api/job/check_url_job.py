from urllib.parse import unquote

from src.models.api.job import Job


class CheckUrlJob(Job):
    url: str
    timeout: int = 2  # We default to 2 seconds

    @property
    def unquoted_url(self):
        """Decoded url"""
        return unquote(self.url)
