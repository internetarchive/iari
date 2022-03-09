import logging
from typing import List

from pydantic import BaseModel
from pywikibot.scripts.generate_user_files import pywikibot
from wikibaseintegrator.wbi_config import config as wbi_config

import config
from src.models.exceptions import DebugExit
from src.helpers import console
from src.models.wikimedia.enums import WikimediaSite
from src.models.wikimedia.wikipedia.wikipedia_page import WikipediaPage

logging.basicConfig(level=config.loglevel)


class WcdImportBot(BaseModel):
    max_count: int = 10
    wikibase_url: str
    mediawiki_api_url: str
    mediawiki_index_url: str
    sparql_endpoint_url: str
    language_code: str = "en"
    wikimedia_site: WikimediaSite = WikimediaSite.WIKIPEDIA

    # pseudo code
    # for each pageid in range(1,1000)
        # get wikipedia page
        # extract templates
        # iterate templates we support
        # create reference objects for each one
        # generate item in wcd
    def __setup_wbi__(self):
        wbi_config['WIKIBASE_URL'] = self.wikibase_url
        wbi_config['MEDIAWIKI_API_URL'] = self.mediawiki_api_url
        wbi_config['MEDIAWIKI_INDEX_URL'] = self.mediawiki_index_url
        wbi_config['SPARQL_ENDPOINT_URL'] = self.sparql_endpoint_url

    def get_pages_by_range(self) -> List[WikipediaPage]:
        pages = []
        count = 0
        # https://stackoverflow.com/questions/59605802/
        # use-pywikibot-to-download-complete-list-of-pages-from-a-mediawiki-server-without
        site = pywikibot.Site(code=self.language_code, fam=self.wikimedia_site.value)
        for page in site.allpages(namespace=0):
            if count == self.max_count:
                break
            count += 1
            console.print(count)
            console.print(page)
            raise DebugExit()
            pages.append(page)
        return pages
