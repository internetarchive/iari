import logging

import config
from src import WcdImportBot

logging.basicConfig(level=config.loglevel)
wcdimportbot = WcdImportBot()
wcdimportbot.run()
