from typing import Any, Dict, Optional

from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo
from src.models.v2.job.article_job_v2 import ArticleJobV2


class ArticleFileIoV2(FileIo):

    data: Optional[Dict[str, Any]] = None
    subfolder: str = "articlesV2/"
    job: Optional[ArticleJobV2]

    # we override FileIo::filename property to provide custom one for article
    @property
    def filename(self) -> str:
        # raise NotFoundError()
        if not self.job:
            raise MissingInformationError("self.job undefined")
        # we got a job, generate the iari_id
        self.job.get_mediawiki_ids()
        filename = f"{self.job.iari_id}.json"
        return filename
