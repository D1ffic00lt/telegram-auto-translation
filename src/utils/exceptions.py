__all__ = (
    "TranslationException",
    "APIException"
)


class TranslationException(Exception):
    pass


class APIException(TranslationException):
    pass
