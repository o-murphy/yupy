from dataclasses import dataclass
from typing import Sized, TypeVar, Protocol, runtime_checkable

from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('ISizedSchema', 'SizedSchema')

_T = TypeVar('_T', covariant=True)
_S = TypeVar('_S')


@runtime_checkable
class ISizedSchema(Protocol[_T]):

    def length(self, limit: int, message: ErrorMessage = locale["length"]) -> _T: ...

    def min(self, limit: int, message: ErrorMessage = locale["min"]) -> _T: ...

    def max(self, limit: int, message: ErrorMessage = locale["max"]) -> _T: ...


@dataclass
class SizedSchema(Schema[_S]):
    _Self = TypeVar('_Self', bound='SizedSchema')

    def length(self: _Self, limit: int, message: ErrorMessage = locale["length"]) -> _Self:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) != limit:
                raise ValidationError(Constraint("length", message, limit), invalid_value=x)

        return self.test(_)

    def min(self: _Self, limit: int, message: ErrorMessage = locale["min"]) -> _Self:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) < limit:
                raise ValidationError(Constraint("min", message, limit), invalid_value=x)

        return self.test(_)

    def max(self: _Self, limit: int, message: ErrorMessage = locale["max"]) -> _Self:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) > limit:
                raise ValidationError(Constraint("max", message, limit), invalid_value=x)

        return self.test(_)
