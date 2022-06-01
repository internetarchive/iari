from src.models.wikicitations.enums import WCDItem
from src.models.wikicitations.itemtypes.base_item_type import BaseItemType


class WikipediaReference(BaseItemType):
    wcditem = WCDItem.WIKIPEDIA_REFERENCE
