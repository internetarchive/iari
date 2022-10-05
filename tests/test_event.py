from src.models.wikimedia.enterprise_api.event import WikimediaEvent


class TestEvent:
    def test_instantiation(self):
        data = {
            "$schema": "/mediawiki/recentchange/1.0.0",
            "meta": {
                "uri": "https://commons.wikimedia.org/wiki/File:ISS067-E-76350_-_View_of_Earth.jpg",
                "request_id": "a4f9d604-ef20-4047-931b-8652b0856de5",
                "id": "fd131933-3d22-4322-a175-6a93e4bcc048",
                "dt": "2022-10-04T15:43:17Z",
                "domain": "commons.wikimedia.org",
                "stream": "mediawiki.recentchange",
                "topic": "eqiad.mediawiki.recentchange",
                "partition": 0,
                "offset": 4209897148,
            },
            "id": 2025605735,
            "type": "edit",
            "namespace": 6,
            "title": "File:ISS067-E-76350 - View of Earth.jpg",
            "comment": "/* wbsetlabel-add:1|en */ View of Earth taken during ISS Expedition 67",
            "timestamp": 1664898197,
            "bot": True,
        }
        WikimediaEvent(**data)
