import logging
import os
from typing import List

# Login credentials to WikiCitations
user = ""
pwd = ""

# Login credentials to sandbox.wiki
sandbox_user = "So9q@test"
# https://medium.datadriveninvestor.com/accessing-github-secrets-in-python-d3e758d8089b
sandbox_pwd = os.environ["ia_sandbox"]

# Login to rabbitmq bitnami container
rabbitmq_username = "user"
rabbitmq_password = "bitnami"

# Settings:
cache_host: str = "127.0.0.1"
cache_port: int = 8888
compare_references = False
assume_persons_without_role_are_authors = True
debug_unsupported_templates = False
include_url_in_hash_algorithm = True
loglevel = logging.ERROR
press_enter_to_continue = False
user_agent = "wcdimportbot 2.0.0-alpha3"
sparql_sync_waiting_time_in_seconds = 5
check_if_page_has_been_uploaded_via_sparql = True
print_debug_json = False
article_update_delay_in_minutes = 24 * 60  # 24 hours
reference_update_delay_in_minutes = 96 * 60  # 96 hours
title_allow_list = [
    "Easter island",
]
max_events_during_testing = 10
use_sandbox_wikibase_backend_for_wikicitations_api = True

# Supported templates
citation_template = [
    "citation",  # see https://en.wikipedia.org/wiki/Template:Citation
    ]
citeq_templates = [
    "cite q",
    "citeq",  # alias
]
cs1_templates = [
    # CS1 templates:
    "cite arxiv",
    "cite av media notes",
    "cite av media",
    "cite biorxiv",
    "cite book",
    "cite cite seerx",
    "cite conference",
    "cite dictionary",  # alias for cite encyclopedia
    "cite encyclopedia",
    "cite episode",
    "cite interview",
    "cite journal",
    "cite magazine",
    "cite mailing list",
    "cite map",
    "cite news",
    "cite newsgroup",
    "cite podcast",
    "cite press release",
    "cite report",
    "cite serial",
    "cite sign",
    "cite speech",
    "cite ssrn",
    "cite techreport",
    "cite thesis",
    "cite web",
]
isbn_template = [
    "isbn",
]
url_template = [
    "url",
]
supported_citation_templates: List[str] = []
for list_ in [citation_template, citeq_templates, cs1_templates, isbn_template, url_template]:
    supported_citation_templates.extend(list_)
bare_url_regex = (
    # There are about 10 different ones but we don't care
    # for now which one is in use
    "bare url"
)

wikibase_url = "https://wikicitations.wiki.opencura.com"
mediawiki_api_url = wikibase_url + "/w/api.php"
mediawiki_index_url = wikibase_url + "/w/index.php"
sparql_endpoint_url = wikibase_url + "/query/sparql"
wikibase_rdf_entity_prefix = "http://wikicitations.wiki.opencura.com/entity/"
