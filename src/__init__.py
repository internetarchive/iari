#!/usr/bin/env python3
"""
The purpose of this API is
* to analyze a Wikipedia article based on the title, wikimedia site and language code
* to easily link between a Wikipedia article and the corresponding Wikipedia Citations Database item

Inspired by: https://rapidapi.com/blog/how-to-build-an-api-in-python/ and
https://medium.com/analytics-vidhya/how-to-test-flask-applications-aef12ae5181c and
https://github.com/pallets/flask/blob/1.1.2/examples/tutorial/flaskr/__init__.py
"""
import logging
import os

from flask import Flask  # type: ignore
from flask_restful import Api, Resource  # type: ignore

from src.models.identifiers_checking.url import TestdeadlinkKeyError
from src.views.check_doi import CheckDoi
from src.views.check_url import CheckUrl
from src.views.statistics.all import All
from src.views.statistics.article import Article
from src.views.statistics.pdf import Pdf
from src.views.statistics.reference import Reference
from src.views.statistics.references import References
from src.views.statistics.xhtml import Xhtml

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

if not os.getenv("TESTDEADLINK_KEY"):
    raise TestdeadlinkKeyError(
        "No testdeadlink key found, please put it in the environment"
    )

app = Flask(__name__)
# We use a prefix here to enable us to stabilize the api over time
# and bump the version when making breaking changes
api = Api(app, prefix="/v2")

# Here we link together the API views and endpoint urls
# api.add_resource(LookupByWikidataQid, "/wikidata-qid/<string:qid>")
api.add_resource(CheckUrl, "/check-url")
api.add_resource(CheckDoi, "/check-doi")
api.add_resource(Article, "/statistics/article")
api.add_resource(All, "/statistics/all")
api.add_resource(References, "/statistics/references")
api.add_resource(Reference, "/statistics/reference/<string:reference_id>")
api.add_resource(Pdf, "/statistics/pdf")
api.add_resource(Xhtml, "/statistics/xhtml")
