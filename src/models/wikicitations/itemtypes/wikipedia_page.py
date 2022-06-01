from src.models.wikicitations.enums import WCDItem
from src.models.wikicitations.itemtypes.base_item_type import BaseItemType


class WikipediaPage(BaseItemType):
    wcditem = WCDItem.WIKIPEDIA_PAGE
