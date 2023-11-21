from urllib.parse import unquote

from src.models.api.job import Job


class UrlArchiveJob(Job):
    url: str

    @property
    def unquoted_url(self):
        """Decoded url"""
        return unquote(self.url)
