from unittest import TestCase

from pydantic import ValidationError

from src.models.api.enums import Subset
from src.models.api.job import Job
from src.models.wikimedia.enums import WikimediaSite


class TestJob(TestCase):
    def test_urldecode_title(self):
        job = Job(title="%20")
        job.urldecode_title()
        assert job.title == " "

    def test_site(self):
        job = Job(title="", site="wikipedia")
        assert job.site == WikimediaSite.wikipedia

    def test_get_page_id(self):
        job = Job(title="Test", site="wikipedia", lang="en")
        job.get_page_id()
        assert job.page_id == 11089416

    def test_refresh(self):
        job = Job(title="Test", site="wikipedia", lang="en")
        assert job.refresh is False
        job = Job(title="Test", site="wikipedia", lang="en", refresh=True)
        assert job.refresh is True
        with self.assertRaises(ValidationError):
            Job(title="Test", site="wikipedia", lang="en", refresh="123")

    def test_subset(self):
        job = Job(title="Test", site="wikipedia", lang="en")
        assert job.subset is None
        job = Job(
            title="Test",
            site="wikipedia",
            lang="en",
            refresh=True,
            subset=Subset.malformed,
        )
        assert job.subset == Subset.malformed
        job = Job(
            title="Test",
            site="wikipedia",
            lang="en",
            refresh=True,
            subset=Subset.not_found,
        )
        assert job.subset == Subset.not_found
        with self.assertRaises(ValidationError):
            Job(title="Test", site="wikipedia", lang="en", refresh=True, subset="123")
