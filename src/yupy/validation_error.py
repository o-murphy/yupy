from dataclasses import dataclass, field
from typing import Generator, Any, List, Optional, Union

from yupy.locale import get_error_message, ErrorMessage

__all__ = (
    'ValidationError',
    'Constraint',
    '_EMPTY_MESSAGE_',
)

_EMPTY_MESSAGE_: ErrorMessage = ""


@dataclass
class Constraint:
    type: str
    args: Any
    message: ErrorMessage = field(repr=False)

    def __init__(self,
                 type: Optional[str],
                 message: Optional[ErrorMessage] = _EMPTY_MESSAGE_,
                 *args: Any,
                 ):
        self.type = type or "undefined"
        self.args = args
        if message is None or message is _EMPTY_MESSAGE_: # Check against _EMPTY_MESSAGE_ for default behavior
            self.message = get_error_message("undefined")
        else:
            self.message = message

    @property
    def format_message(self) -> str:
        if callable(self.message):
            return self.message(self.args)
        return self.message


class ValidationError(ValueError):
    def __init__(
            self, constraint: Optional[Constraint] = None, path: str = "",
            errors: Optional[List['ValidationError']] = None,
            invalid_value: Optional[Any] = None, *args) -> None:
        if not constraint:
            self.constraint = Constraint("undefined")
        else:
            self.constraint = constraint
        self.path = path
        self._errors: List[ValidationError] = errors or []
        self.invalid_value: Optional[Any] = invalid_value
        super().__init__(self.path, self.constraint, self._errors, *args)

    def __str__(self) -> str:
        return "(path=%r, constraint=%r, message=%r)" % (self.path, self.constraint, self.constraint.format_message)

    def __repr__(self) -> str:
        return "ValidationError%s" % self.__str__()

    @property
    def errors(self) -> Generator['ValidationError', None, None]:
        yield self
        for error in self._errors:
            yield from error.errors

    @property
    def message(self) -> str:
        return "%r:%s" % (self.path, self.constraint.format_message)

    @property
    def messages(self) -> Generator[Union[property, str], None, None]:
        for e in self.errors:
            yield e.message
