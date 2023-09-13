from urllib.parse import unquote

from src.models.api.job import Job


class UrlsJob(Job):
    url: str
    timeout: int = 2  # We default to 2 seconds
    debug: bool = False
    blocks: bool = False
    html: bool = False
    xml: bool = False
    json_: bool = False

    @property
    def url_list(self):
        """Decoded urls"""
        from flask import request

        return request.args.getlist("url")

    @property
    def url_dict(self):
        """Decoded urls"""
        from flask import request

        url_list = request.args.getlist("url")
        url_dict = {url_list[i]: {} for i in range(0, len(url_list))}

        return url_dict
