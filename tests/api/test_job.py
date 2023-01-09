from unittest import TestCase

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
