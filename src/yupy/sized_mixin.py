from typing import Generic, Sized, Self, TypeVar

from yupy.locale import locale
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('SizedMixin',)

_T = TypeVar('_T')

class SizedMixin(Generic[_T]):
    def length(self: Self, limit: int, message: ErrorMessage = locale["length"]) -> Self:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) != limit:
                raise ValidationError(Constraint("length", limit, message))
        return self.test(_)

    def min(self: Self, limit: int, message: ErrorMessage = locale["min"]) -> Self:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) < limit:
                raise ValidationError(Constraint("min", limit, message))
        return self.test(_)

    def max(self: Self, limit: int, message: ErrorMessage = locale["max"]) -> Self:
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) > limit:
                raise ValidationError(Constraint("max", limit, message))
        return self.test(_)
