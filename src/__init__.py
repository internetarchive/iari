"""
The purpose of this API is
* to analyze a Wikipedia article based on the title, wikimedia site and language code
* to easily link between a Wikipedia article and the corresponding Wikipedia Citations Database item

Inspired by: https://rapidapi.com/blog/how-to-build-an-api-in-python/ and
https://medium.com/analytics-vidhya/how-to-test-flask-applications-aef12ae5181c and
https://github.com/pallets/flask/blob/1.1.2/examples/tutorial/flaskr/__init__.py
"""
import logging

from flask import Flask  # type: ignore
from flask_restful import Api, Resource  # type: ignore

import config
from src.views.check_doi import CheckDoi
from src.views.check_url import CheckUrl
from src.views.check_url_archive import CheckUrlArchive
from src.views.check_urls import CheckUrls
from src.views.statistics.all import All
from src.views.statistics.article import Article
from src.views.statistics.pdf import Pdf
from src.views.statistics.reference import Reference
from src.views.statistics.references import References
from src.views.statistics.xhtml import Xhtml
from src.views.version import Version

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# We use a prefix here to enable us to stabilize the api over time
# and bump the version when making breaking changes
api = Api(app, prefix="/v2")

# Here we link together the API views and endpoint urls
# api.add_resource(LookupByWikidataQid, "/wikidata-qid/<string:qid>")
api.add_resource(Version, "/version")
api.add_resource(CheckUrls, "/check-urls")
api.add_resource(CheckUrl, "/check-url")
api.add_resource(CheckUrlArchive, "/check-url-archive")
api.add_resource(CheckDoi, "/check-doi")
api.add_resource(Article, "/statistics/article")
api.add_resource(All, "/statistics/all")
api.add_resource(References, "/statistics/references")
api.add_resource(Reference, "/statistics/reference/<string:reference_id>")
api.add_resource(Pdf, "/statistics/pdf")
api.add_resource(Xhtml, "/statistics/xhtml")
# return app_
# api.add_resource(
#     AddJobToQueue, "/add-job"
# )  # ?lang=<string:language_code>&site=<string:wikimedia_site>&title=<string:title>")
