#!/usr/bin/env python
import logging

try:
    import config
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "config.py not found. Please follow the instructions in the README about how to set up the config.py file"
    )
from src import WcdImportBot
from src.models.wikibase.enums import SupportedWikibase

logging.basicConfig(level=config.loglevel)
# This hides exceptions about modification failed from wikibaseintegrator
logging.getLogger("wikibaseintegrator").setLevel(level=logging.CRITICAL)
wcdimportbot = WcdImportBot(target_wikibase=SupportedWikibase.IASandboxWikibase)
wcdimportbot.run()
