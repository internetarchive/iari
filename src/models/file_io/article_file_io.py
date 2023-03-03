import logging
from typing import Any, Dict

from src.models.api.job.article_job import ArticleJob
from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo

logger = logging.getLogger(__name__)


class ArticleFileIo(FileIo):
    data: Dict[str, Any] = dict()
    subfolder = "articles/"
    job: ArticleJob

    @property
    def filename(self) -> str:
        if not self.job:
            raise MissingInformationError()
        # we got a job, generate the wari_id
        self.job.get_page_id()
        if not self.job.page_id:
            raise MissingInformationError()
        wari_id = (
            f"{self.job.lang.value}." f"{self.job.site.value}.org.{self.job.page_id}"
        )
        filename = f"{wari_id}.json"
        return filename
