from typing import Any, Dict, Optional

from src.v3.models.api.job.article_job import ArticleJob
from src.v3.models.exceptions import MissingInformationError
from src.v3.models.file_io import FileIo


class ArticleFileIo(FileIo):
    data: Dict[str, Any] = dict()
    subfolder = "articles/"
    job: Optional[ArticleJob]

    @property
    def filename(self) -> str:
        if self.wari_id:
            filename = f"{self.wari_id}.json"
            return filename
        else:
            if not self.job:
                raise MissingInformationError()
            # we got a job, generate the wari_id
            self.job.get_page_id()
            if not self.job.page_id:
                raise MissingInformationError()
            wari_id = f"{self.job.lang}.{self.job.domain.value}.{self.job.page_id}"
            filename = f"{wari_id}.json"
            return filename
