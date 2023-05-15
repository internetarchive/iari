from urllib.parse import unquote

from src.v3.models.api.job import Job


class UrlJob(Job):
    url: str
    timeout: int = 2  # We default to 2 seconds

    @property
    def unquoted_url(self):
        """Decoded url"""
        return unquote(self.url)
