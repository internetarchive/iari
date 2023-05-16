from enum import Enum

# class WikidataProperty(Enum):
#     MAIN_SUBJECT = "P921"
#     DETERMINATION_METHOD = "P459"
#     STATED_AS = "P1932"


# class WikidataItem(Enum):
#     CROSSREF = "Q5188229"


# class WikidataNamespaceLetters(Enum):
#     PROPERTY = "P"
#     ITEM = "Q"
#     LEXEME = "L"
#     # FORM = "F"
#     # SENSE = "S"


# class WikimediaLanguage(Enum):
#     DANISH = "Q9035"
#     SWEDISH = "Q9027"
#     BOKMAL = "Q25167"
#     ENGLISH = "Q1860"
#     FRENCH = "Q150"
#     RUSSIAN = "Q7737"
#     ESTONIAN = "Q9072"
#     MALAYALAM = "Q36236"
#     LATIN = "Q397"
#     HEBREW = "Q9288"
#     BASQUE = "Q8752"
#     GERMAN = "Q188"
#     BENGALI = "Q9610"
#     CZECH = "Q9056"


class WikimediaDomain(Enum):
    # For now we only support Wikipedia
    wikipedia = "wikipedia.org"


# class WikimediaEditType(Enum):
#     NEW = "new"
#     EDIT = "edit"
#     LOG = "log"
#     CATEGORIZE = "categorize"
#     UNKNOWN = "142"


# class ReferenceType(Enum):
#     CLEAN_SUPPORTED_CITATION_REFERENCE = auto() # cite q, cs1, citation
#     PLAIN_TEXT_REFERENCE_WITH_CS1_TEMPLATE = auto()
#     PLAIN_TEXT_REFERENCE_WITH_BARE_URL_TEMPLATE = auto()
#     PLAIN_TEXT_REFERENCE_WITH_ISBN_TEMPLATE = auto()
#     PLAIN_TEXT_REFERENCE_WITH_A_SUPPORTED_IDENTIFIER = auto() # URL is a supported identifier


class AnalyzerReturn(Enum):
    IS_REDIRECT = "No statistic available because this is a redirect."
    NOT_FOUND = "Article title not found."
