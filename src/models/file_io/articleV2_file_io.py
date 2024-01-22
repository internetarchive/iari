from typing import Any, Dict, Optional

from src.models.job.articleV2_job import ArticleV2Job
from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo


class ArticleV2FileIo(FileIo):
    data: Optional[Dict[str, Any]] = None
    subfolder = "articlesV2/"
    job: Optional[ArticleV2Job]

    @property
    def filename(self) -> str:
        if not self.job:
            raise MissingInformationError()
        # we got a job, generate the iari_id
        self.job.get_ids_from_mediawiki_api()
        filename = f"{self.job.iari_id}.json"
        return filename
