import logging
import re

# Settings:
link_extraction_regex = re.compile(
    r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?"
)
subdirectory_for_json = "json/"  # create it manually before running the api
loglevel = logging.ERROR
user_agent = "IARI, see https://github.com/internetarchive/iari"
