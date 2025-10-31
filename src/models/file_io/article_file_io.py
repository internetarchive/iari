from typing import Any, Dict, Optional

from src.models.api.job.article_job import ArticleJob
from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo


class ArticleFileIo(FileIo):
    data: Optional[Dict[str, Any]] = None
    subfolder: str = "articles/"
    job: Optional[ArticleJob]

    @property
    def filename(self) -> str:
        if not self.job:
            raise MissingInformationError()
        # we got a job, generate the wari_id
        self.job.get_ids_from_mediawiki_api()
        filename = f"{self.job.wari_id}.json"
        return filename
