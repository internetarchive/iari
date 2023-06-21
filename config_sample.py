import logging
import re

# Settings:
# this key is needed to access the testdeadlink endpoint
testdeadlink_key = ""
link_extraction_regex = re.compile(
    r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?"
)
subdirectory_for_json = "json/"  # create it manually before running the api
loglevel = logging.ERROR
user_agent = "IARI, see https://github.com/internetarchive/iari"
