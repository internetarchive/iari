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
from flask_restful import Api  # type: ignore

import config
from src.models.api.get_statistics.get_article_statistics import GetArticleStatistics
from src.models.api.get_statistics.get_url_statistics import GetUrlStatistics

# from src.models.api.add_job_to_queue import AddJobToQueue

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# We use a prefix here to enable us to stabilize the api over time
# and bump the version when making breaking changes
api = Api(app, prefix="/v1")

# api.add_resource(LookupByWikidataQid, "/wikidata-qid/<string:qid>")
api.add_resource(GetUrlStatistics, "/get-urls")
api.add_resource(GetArticleStatistics, "/get-statistics")
# return app_
# api.add_resource(
#     AddJobToQueue, "/add-job"
# )  # ?lang=<string:language_code>&site=<string:wikimedia_site>&title=<string:title>")
