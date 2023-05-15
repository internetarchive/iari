from urllib.parse import unquote

from src.v3.models.api.job import Job


class CheckDoiJob(Job):
    doi: str
    timeout: int = 2

    @property
    def unquoted_doi(self):
        """Decoded url"""
        return unquote(self.doi)
