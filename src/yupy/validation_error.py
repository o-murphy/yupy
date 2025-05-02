from dataclasses import dataclass, field
from typing import Generator, Any, List, Optional, Union, Callable, TypeAlias

__all__ = (
    'ErrorMessage',
    'ValidationError',
    'Constraint',
)


ErrorMessage: TypeAlias = Union[str, Callable[[Any | List[Any]], str]]


@dataclass
class Constraint:

    def __init__(self,
        type: Optional[str],
        message: Optional[ErrorMessage] = None,
        *args: Any,
    ):
        self.type = type
        self.args = args
        if not message:
            from yupy.locale import get_error_message
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
        return f"(path={repr(self.path)}, constraint={self.constraint}, message={repr(self.constraint.format_message)})"

    def __repr__(self) -> str:
        return "ValidationError%s" % self.__str__()

    @property
    def errors(self) -> Generator['ValidationError', None, None]:
        yield self
        for error in self._errors:
            yield from error.errors

    @property
    def message(self) -> str:
        return f"{repr(self.path)}: {self.constraint.format_message}"

    @property
    def messages(self) -> Generator[Union[property, str], None, None]:
        for e in self.errors:
            yield e.message
