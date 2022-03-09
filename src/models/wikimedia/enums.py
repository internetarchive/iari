from enum import Enum


class DeterminationMethod(Enum):
    FUZZY_POWERED_NAMED_ENTITY_RECOGNITION_MATCHER = "Q110733873"


class Property(Enum):
    MAIN_SUBJECT = "P921"
    DETERMINATION_METHOD = "P459"
    STATED_AS = "P1932"


class StatedIn(Enum):
    CROSSREF = "Q5188229"


class WikidataNamespaceLetters(Enum):
    PROPERTY = "P"
    ITEM = "Q"
    LEXEME = "L"
    # FORM = "F"
    # SENSE = "S"


class WikimediaLanguage(Enum):
    DANISH = "Q9035"
    SWEDISH = "Q9027"
    BOKMÅL = "Q25167"
    ENGLISH = "Q1860"
    FRENCH = "Q150"
    RUSSIAN = "Q7737"
    ESTONIAN = "Q9072"
    MALAYALAM = "Q36236"
    LATIN = "Q397"
    HEBREW = "Q9288"
    BASQUE = "Q8752"
    GERMAN = "Q188"
    BENGALI = "Q9610"
    CZECH = "Q9056"


class WikimediaSite(Enum):
    WIKIPEDIA = "wikipedia"


class WikimediaEditType(Enum):
    NEW = "new"
    EDIT = "edit"
    LOG = "log"
    CATEGORIZE = "categorize"
    UNKNOWN = "142"
