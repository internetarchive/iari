from src.models.v2.job import JobV2


class ArticleCacheJobV2(JobV2):

    # the iari id of the article as previously retrieved
    iari_id: str = 0
    article_version: int = 0  # should be 1 or 2
