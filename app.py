"""
The purpose of this API is to easily link between
a Wikipedia article and the corresponding Wikicitations item
https://rapidapi.com/blog/how-to-build-an-api-in-python/
"""
import logging

from flask import Flask # type: ignore
from flask_restful import Api # type: ignore

import config
from src.models.api.add_job_to_queue import AddJobToQueue
from src.models.api.lookup_by_wikidata_qid import LookupByWikidataQid

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)
app = Flask(__name__)
api = Api(app, prefix="/v1")

api.add_resource(LookupByWikidataQid, "/wikidata-qid/<string:qid>")
api.add_resource(
    AddJobToQueue, "/add-job"
)  # ?lang=<string:language_code>&site=<string:wikimedia_site>&title=<string:title>")

if __name__ == "__main__":
    app.run(debug=True)
