from typing import Any, Dict, Optional

from src.models.exceptions import MissingInformationError
from src.models.file_io import FileIo
from src.models.v2.job.article_cache_job_v2 import ArticleCacheJobV2


class ArticleCacheFileIoV2(FileIo):
    data: Optional[Dict[str, Any]] = None

    job: Optional[ArticleCacheJobV2]

    subfolder: str = "articles/"

    # we override FileIo::filename property to provide custom one for cached article
    @property
    def filename(self) -> str:
        # raise NotFoundError()
        if not self.job:
            raise MissingInformationError("self.job undefined")

        # we got a job, file name should be iari_id +".json"
        filename = f"{self.job.iari_id}.json"
        return filename
