import os
from os.path import exists
from unittest import TestCase

import pytest

from src.v2.models.api.job.article_job import ArticleJob
from src.v2.models.api.statistic.article import ArticleStatistics
from src.v2.models.file_io.article_file_io import ArticleFileIo


class TestArticleFileIo(TestCase):
    job = ArticleJob(title="Test", site="wikipedia", lang="en")

    # def test_filename(self):
    #     io = FileIo(job=self.__test_job__)
    #     assert io.filename == "json/en.wikipedia.org:0"
    #     io1 = FileIo(
    #         job=self.__test_job__,
    #         statistics_dictionary=ArticleStatistics(page_id=1).dict(),
    #     )
    #     assert io1.filename == "json/en.wikipedia.org:1"
    #     io2 = FileIo(
    #         job=self.__test_job__,
    #         statistics_dictionary=ArticleStatistics(page_id=1).dict(),
    #     )
    #     io2.job.get_page_id()
    #     assert io2.filename == "json/en.wikipedia.org:11089416"

    # https://stackoverflow.com/questions/73973332/check-if-were-in-a-github-action-tracis-ci-circle-ci-etc-testing-environme
    @pytest.mark.skipif(
        "GITHUB_ACTIONS" in os.environ, reason="test is skipped in GitHub Actions"
    )
    def test_save_to_disk(self):
        io1 = ArticleFileIo(
            job=self.job, data=ArticleStatistics(page_id=1).dict(), testing=True
        )
        print(io1.data)
        io1.write_to_disk()
        assert exists(io1.path_filename) is True

    @pytest.mark.skipif(
        "GITHUB_ACTIONS" in os.environ, reason="test is skipped in GitHub Actions"
    )
    def test_read_from_disk(self):
        stat = ArticleStatistics(page_id=11089416, served_from_cache=True)
        io1 = ArticleFileIo(job=self.job, data=stat, testing=True)
        io1.write_to_disk()
        # we set to None here to check that we actually get the data
        io1.data = None
        io1.read_from_disk()
        if io1.data:
            assert ArticleStatistics(**io1.data) == stat
        else:
            self.fail("no dictionary")
