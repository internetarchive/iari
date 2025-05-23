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
import traceback

from flask import Flask, request  # type: ignore
from flask_restful import Api, Resource  # type: ignore

# from flask_cors import CORS
import config
from src.models.exceptions import MissingInformationError, WikipediaApiFetchError

# legacy endpoints stuff...
from src.views.check_doi import CheckDoi
# from src.views.check_url import CheckUrl
from src.views.check_url_archive import CheckUrlArchive
from src.views.check_urls import CheckUrls
from src.views.statistics.all import All
from src.views.statistics.article import Article
from src.views.statistics.pdf import Pdf
from src.views.statistics.reference import Reference
from src.views.statistics.references import References
from src.views.statistics.xhtml import Xhtml

# new stuff jan 2024
from src.views.v2.article_view_v2 import ArticleV2
from src.views.v2.get_book_reference_v2 import GetBookReferenceV2
from src.views.v2.get_url_info_v2 import GetUrlInfoV2
from src.views.version import Version
# new stuff apr 2024
from src.views.v2.article_cache_view_v2 import ArticleCacheV2
# new stuff jun 2024
from src.views.v2.editref_v2 import EditRefV2
# new stuff jul 2024
from src.views.v2.fetchrefs_v2 import FetchRefsV2
# new stuff oct 2024
from src.views.v2.extract_refs_v2 import ExtractRefsV2
from src.views.v2.ref_insights_v2 import InsightsWebRxV2
# new stuff jan 2025
from src.views.v2.check_url_v2 import CheckUrlV2
# new stuff mar 2025
from src.views.v2.probe_v2 import ProbeV2

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def add_cors_headers(response):
    # Replace "*" with the specific origin(s) you want to allow
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# Register CORS function as an after_request handler
app.after_request(add_cors_headers)

# let's see if we can distinguish which server we are on
server_name = os.getenv('FLASK_SERVER_NAME', 'Unknown Server')

# We use a prefix here to enable us to stabilize the api over time
# and bump the version when making breaking changes
api = Api(app, prefix="/v2")  # NB TODO This pseudo-versioning should be addressed


@app.errorhandler(404)
def not_found(e):
    app.logger.error(f"Endpoint '{request.path}' not found")
    return {
        "error": f"Endpoint '{request.path}' not found",
    }


@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()
    return {"error": "A generic exception occurred", "details": str(e)}

#
# @app.errorhandler(500)
# def handle_exception(e):
#     traceback.print_exc()
#     return {"error": "A 500 exception occurred", "details": str(e)}, 500
#


@app.route('/favicon.ico')
def favicon():
    # app.logger.info("No favicon serve")
    return '', 204  # No Content


# link respective endpoints to API views
api.add_resource(GetUrlInfoV2, "/get_url_info")
api.add_resource(ProbeV2, "/probe")
api.add_resource(GetBookReferenceV2, "/get_book_reference")
api.add_resource(InsightsWebRxV2, "/insights")      # Stephen's and Sawood's numbers
api.add_resource(ExtractRefsV2, "/extract_refs")
api.add_resource(FetchRefsV2, "/fetchrefs")
api.add_resource(EditRefV2, "/editref")

api.add_resource(ArticleV2, "/article")
api.add_resource(ArticleCacheV2, "/article_cache")

api.add_resource(Version, "/version")
api.add_resource(CheckUrls, "/check-urls")
api.add_resource(CheckUrlV2, "/check-url")
api.add_resource(CheckUrlArchive, "/check-url-archive")
api.add_resource(CheckDoi, "/check-doi")
api.add_resource(Article, "/statistics/article")
api.add_resource(All, "/statistics/all")
api.add_resource(References, "/statistics/references")
api.add_resource(Reference, "/statistics/reference/<string:reference_id>")
api.add_resource(Pdf, "/statistics/pdf")
api.add_resource(Xhtml, "/statistics/xhtml")

# api.add_resource(LookupByWikidataQid, "/wikidata-qid/<string:qid>")

# return app_
# api.add_resource(
#     AddJobToQueue, "/add-job"
# )  # ?lang=<string:language_code>&site=<string:wikimedia_site>&title=<string:title>")

#
# @app.errorhandler(Exception)
# def handle_missing_information_error(error):
#     return str(error), 500
