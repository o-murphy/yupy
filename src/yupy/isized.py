from typing import Sized, TypeVar, Protocol

from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('ISized', 'SizedSchema')

_T = TypeVar('_T', covariant=True)
_S = TypeVar('_S')

class ISized(Protocol[_T]):
    def length(self, limit: int, message: ErrorMessage = locale["length"]) -> _T: ...

    def min(self, limit: int, message: ErrorMessage = locale["min"]) -> _T: ...

    def max(self, limit: int, message: ErrorMessage = locale["max"]) -> _T: ...


class SizedSchema(Schema[_S]):
    def length(self, limit: int, message: ErrorMessage = locale["length"]) -> _S:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) != limit:
                raise ValidationError(Constraint("length", limit, message))

        return self.test(_)

    def min(self, limit: int, message: ErrorMessage = locale["min"]) -> _S:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) < limit:
                raise ValidationError(Constraint("min", limit, message))

        return self.test(_)

    def max(self, limit: int, message: ErrorMessage = locale["max"]) -> _S:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) > limit:
                raise ValidationError(Constraint("max", limit, message))

        return self.test(_)
