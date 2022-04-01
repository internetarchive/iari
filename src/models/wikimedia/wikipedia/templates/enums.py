from enum import Enum, auto


class EnglishWikipediaTemplatePersonRole(Enum):
    AUTHOR = "author"
    EDITOR = "editor"
    HOST = "host"
    INTERVIEWER = "interviewer"
    TRANSLATOR = "translator"
    UNKNOWN = auto()
