from bs4 import Tag
from pydantic import BaseModel


class XhtmlLink(BaseModel):
    """This models an xhtml link"""

    context: Tag  # this is usually the <a>
    href: str  # the link itself
    title: str = ""
    parent: Tag  # this is the larger context of the link e.g. a <p> or <div> or <pre>

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    def get_dict(self):
        """This is needed to enable json encoding in the API"""
        return {
            "context": str(self.context),
            "parent": str(self.parent),
            "title": self.title,
            "href": self.href,
        }
