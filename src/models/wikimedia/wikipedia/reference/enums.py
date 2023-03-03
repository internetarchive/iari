from enum import Enum, auto


class WikipediaTemplatePersonRole(Enum):
    pass


class EnglishWikipediaTemplatePersonRole(WikipediaTemplatePersonRole):
    AUTHOR = "author"
    EDITOR = "editor"
    HOST = "host"
    INTERVIEWER = "interviewer"
    TRANSLATOR = "translator"
    UNKNOWN = auto()


class ReferenceType(Enum):
    GENERAL = "general"  # this can be from anywhere in the article
    FOOTNOTE = "footnote"  # this is footnotes marked up with <ref></ref>


class FootnoteSubtype(Enum):
    NAMED = "named"  # this an empty named reference like <ref name="test"/>
    CONTENT = "content"  # this is footnotes marked up with <ref></ref>
