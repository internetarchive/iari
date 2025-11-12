import logging
import re

# Settings:

regex_url_link_extraction = re.compile(
    r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?"
)
regex_url_wiki = re.compile(
    r"https?://(\w+)\.(\w+\.\w+)/wiki/(.+)"
)

iari_cache_dir = "json/"  # relative to top of tree; create it manually before running api

# loglevel = logging.ERROR
loglevel = logging.DEBUG
# loglevel = logging.INFO

user_agent = "IARI, see https://github.com/internetarchive/iari"
