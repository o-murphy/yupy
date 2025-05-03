from dataclasses import dataclass
from typing import Sized, TypeVar, Protocol, runtime_checkable

from typing_extensions import Self

from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('ISizedSchema', 'SizedSchema')

_P = TypeVar('_P', covariant=True)
_T = TypeVar('_T')


@runtime_checkable
class ISizedSchema(Protocol[_P]):

    def length(self, limit: int, message: ErrorMessage = locale["length"]) -> _P: ...

    def min(self, limit: int, message: ErrorMessage = locale["min"]) -> _P: ...

    def max(self, limit: int, message: ErrorMessage = locale["max"]) -> _P: ...


@dataclass
class SizedSchema(Schema[_T]):

    def length(self, limit: int, message: ErrorMessage = locale["length"]) -> Self:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) != limit:
                raise ValidationError(Constraint("length", message, limit), invalid_value=x)

        return self.test(_)

    def min(self, limit: int, message: ErrorMessage = locale["min"]) -> Self:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) < limit:
                raise ValidationError(Constraint("min", message, limit), invalid_value=x)

        return self.test(_)

    def max(self, limit: int, message: ErrorMessage = locale["max"]) -> Self:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) > limit:
                raise ValidationError(Constraint("max", message, limit), invalid_value=x)

        return self.test(_)
