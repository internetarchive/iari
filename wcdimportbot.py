#!/usr/bin/env python
import logging

try:
    import config
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "config.py not found. Please follow the instructions in the README about how to set up the config.py file"
    )
from src import WcdImportBot

# Found here https://github.com/pika/pika/blob/1.0.1/examples/basic_consumer_threaded.py
LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)

logging.basicConfig(level=config.loglevel, format=LOG_FORMAT)
# This hides exceptions about modification failed from wikibaseintegrator
logging.getLogger("wikibaseintegrator").setLevel(level=logging.CRITICAL)
wcdimportbot = WcdImportBot()
wcdimportbot.run()
