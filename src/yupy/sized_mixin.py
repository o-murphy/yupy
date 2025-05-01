from typing import Sized, TypeVar

from yupy.ischema import ISchema
from yupy.locale import locale
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('SizedMixin',)

_ST = TypeVar('_ST')


class SizedMixin(ISchema[_ST]):
    def length(self, limit: int, message: ErrorMessage = locale["length"]) -> 'Self':
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) != limit:
                raise ValidationError(Constraint("length", limit, message))

        return self.test(_)

    def min(self, limit: int, message: ErrorMessage = locale["min"]) -> 'Self':
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) < limit:
                raise ValidationError(Constraint("min", limit, message))

        return self.test(_)

    def max(self, limit: int, message: ErrorMessage = locale["max"]) -> 'Self':
        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) > limit:
                raise ValidationError(Constraint("max", limit, message))

        return self.test(_)
