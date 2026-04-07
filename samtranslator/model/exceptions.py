from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Sequence
from enum import Enum
from typing import Any, Union


class ExpectedType(Enum):
    MAP = ("map", dict)
    LIST = ("list", list)
    STRING = ("string", str)
    INTEGER = ("integer", int)
    BOOLEAN = ("boolean", bool)


class ExceptionWithMessage(ABC, Exception):
    @property
    @abstractmethod
    def message(self) -> str:
        """Return the exception message."""

    @property
    def metadata(self) -> dict[str, Any] | None:
        """Return the exception metadata."""


class InvalidDocumentException(ExceptionWithMessage):
    """Exception raised when the given document is invalid and cannot be transformed.

    Attributes:
        message -- explanation of the error
        metadata -- a dictionary of metadata (key, value pair)
        causes -- list of errors which caused this document to be invalid
    """

    def __init__(self, causes: Sequence[ExceptionWithMessage]) -> None:
        self._causes = list(causes)
        # Sometimes, the same error could be raised from different plugins,
        # so here we do a deduplicate based on the message:
        self._causes = list({cause.message: cause for cause in self._causes}.values())

    @property
    def message(self) -> str:
        pass

    @property
    def metadata(self) -> dict[str, list[Any]]:
        # Merge metadata in each exception to one single metadata dictionary
        pass

    @property
    def causes(self) -> Sequence[ExceptionWithMessage]:
        pass


class DuplicateLogicalIdException(ExceptionWithMessage):
    """Exception raised when a transformation adds a resource with a logical id which already exists.
    Attributes:
        message -- explanation of the error
    """

    def __init__(self, logical_id: str, duplicate_id: str, resource_type: str) -> None:
        self._logical_id = logical_id
        self._duplicate_id = duplicate_id
        self._type = resource_type

    @property
    def message(self) -> str:
        pass


class InvalidTemplateException(ExceptionWithMessage):
    """Exception raised when the template structure is invalid

    Attributes
        message -- explanation of the error
    """

    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self) -> str:
        pass


class InvalidResourceException(ExceptionWithMessage):
    """Exception raised when a resource is invalid.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, logical_id: Union[str, list[str]], message: str, metadata: dict[str, Any] | None = None) -> None:
        self._logical_id = logical_id
        self._message = message
        self._metadata = metadata

    def __lt__(self, other):  # type: ignore[no-untyped-def]
        return self._logical_id < other._logical_id

    @property
    def message(self) -> str:
        pass

    @property
    def metadata(self) -> dict[str, Any] | None:
        pass


class InvalidResourcePropertyTypeException(InvalidResourceException):
    def __init__(
        self,
        logical_id: str,
        key_path: str,
        expected_type: ExpectedType | None,
        message: str | None = None,
    ) -> None:
        message = message or self._default_message(key_path, expected_type)
        super().__init__(logical_id, message)

        self.key_path = key_path

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return self.message

    @staticmethod
    def _default_message(key_path: str, expected_type: ExpectedType | None) -> str:
        pass


class InvalidResourceAttributeTypeException(InvalidResourceException):
    def __init__(
        self,
        logical_id: str,
        key_path: str,
        expected_type: ExpectedType | None,
        message: str | None = None,
    ) -> None:
        message = message or self._default_message(logical_id, key_path, expected_type)
        super().__init__(logical_id, message)

    @staticmethod
    def _default_message(logical_id: str, key_path: str, expected_type: ExpectedType | None) -> str:
        pass


class InvalidEventException(ExceptionWithMessage):
    """Exception raised when an event is invalid.

    Attributes:
        message -- explanation of the error
    """

    # Note: event_id should not be None, but currently there are too many
    # usage of this class with `event_id` being Optional.
    # TODO: refactor the code to make type correct.
    def __init__(self, event_id: str | None, message: str) -> None:
        self._event_id = event_id
        self._message = message

    @property
    def message(self) -> str:
        pass


def prepend(exception, message, end=": "):  # type: ignore[no-untyped-def]
    """Prepends the first argument (i.e., the exception message) of the a BaseException with the provided message.
    Useful for reraising exceptions with additional information.

    :param BaseException exception: the exception to prepend
    :param str message: the message to prepend
    :param str end: the separator to add to the end of the provided message
    :returns: the exception
    """
    exception.args = exception.args or ("",)
    exception.args = (message + end + exception.args[0], *exception.args[1:])
    return exception
