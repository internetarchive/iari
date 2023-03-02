from os.path import exists
from unittest import TestCase

from src.models.api import ArticleStatistics
from src.models.api.job import Job
from src.models.file_io import FileIo


class TestFileIo(TestCase):
    @property
    def __test_job__(self):
        return Job(title="Test", site="wikipedia", lang="en")

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

    def test_save_to_disk(self):
        io1 = FileIo(
            job=self.__test_job__,
            statistics_dictionary=ArticleStatistics(page_id=1).dict(),
        )
        print(io1.data)
        io1.write_to_disk()
        assert exists(io1.filename) is True

    def test_read_from_disk(self):
        stat = ArticleStatistics(
            page_id=11089416, served_from_cache=True, refreshed_now=False
        )
        io1 = FileIo(job=self.__test_job__, statistics_dictionary=stat)
        io1.write_to_disk()
        # we set to None here to check that we actually get the data
        io1.statistics_dictionary = None
        io1.read_from_disk()
        if io1.statistics_dictionary:
            assert ArticleStatistics(**io1.statistics_dictionary) == stat
        else:
            self.fail("no dictionary")
