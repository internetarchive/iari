from enum import Enum, auto


class Role(Enum):
    AUTHOR = auto()
    EDITOR = auto()
    HOST = auto()
    INTERVIEWER = auto()
    TRANSLATOR = auto()
    UNKNOWN = auto()
