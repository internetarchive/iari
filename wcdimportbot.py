#!/usr/bin/env python
import logging

from src.models.wikibase.wikicitations_wikibase import WikiCitationsWikibase

try:
    import config
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "config.py not found. Please follow the instructions in the README about how to set up the config.py file"
    )
from src import WcdImportBot

logging.basicConfig(level=config.loglevel)
wcdimportbot = WcdImportBot(wikibase=WikiCitationsWikibase())
wcdimportbot.run()
