import logging
from fastapi import FastAPI
from fastapi import APIRouter

import config

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)

app = FastAPI()

# We use a prefix here to enable us to stabilize the API over time
# and bump the version when making breaking changes
router = APIRouter(prefix="/v2")
app.include_router(router)

# v2
from src.v2.views.check_doi import CheckDoi
from src.v2.views.check_url import CheckUrl
from src.v2.views.statistics.all import All
from src.v2.views.statistics.article import Article
from src.v2.views.statistics.pdf import Pdf
from src.v2.views.statistics.reference import Reference
from src.v2.views.statistics.references import References
from src.v2.views.statistics.xhtml import Xhtml

router.add_api_route("/check-url", CheckUrl())
router.add_api_route("/check-doi", CheckDoi())
router.add_api_route("/statistics/article", Article())
router.add_api_route("/statistics/all", All())
router.add_api_route("/statistics/references", References())
router.add_api_route("/statistics/reference/{reference_id}", Reference())
router.add_api_route("/statistics/pdf", Pdf())
router.add_api_route("/statistics/xhtml", Xhtml())

# v3
from src.v3.views.check_doi import CheckDoi as CheckDoi_v3
from src.v3.views.check_url import CheckUrl as CheckUrl_v3
from src.v3.views.statistics.article import Article as Article_v3
from src.v3.views.statistics.pdf import Pdf as Pdf_v3
from src.v3.views.statistics.reference import Reference as Reference_v3
from src.v3.views.statistics.references import References as References_v3
from src.v3.views.statistics.xhtml import Xhtml as Xhtml_v3

router_v3 = APIRouter(prefix="/v3")
app.include_router(router_v3)

router_v3.add_api_route("/check-url", CheckUrl_v3())
router_v3.add_api_route("/check-doi", CheckDoi_v3())
router_v3.add_api_route("/statistics/article", Article_v3())
router_v3.add_api_route("/statistics/references", References_v3())
router_v3.add_api_route("/statistics/reference/{reference_id}", Reference_v3())
router_v3.add_api_route("/statistics/pdf", Pdf_v3())
router_v3.add_api_route("/statistics/xhtml", Xhtml_v3())
