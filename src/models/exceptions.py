class AmbiguousDateError(BaseException):
    pass


class DebugExit(BaseException):
    pass


class MissingInformationError(BaseException):
    pass


class MoreThanOneNumberError(BaseException):
    pass


class MultipleTemplateError(BaseException):
    pass


class NotLoggedInError(BaseException):
    pass


class NotSupportedError(BaseException):
    pass


class TimeParseException(BaseException):
    pass


class WikibaseError(BaseException):
    pass


class WikipediaApiFetchError(BaseException):
    pass


class NoChannelError(BaseException):
    pass


class ResolveError(BaseException):
    pass


class MultipleQidError(BaseException):
    pass


class MultipleIsbnError(BaseException):
    pass


class MultipleDoiError(BaseException):
    pass
