from typing import TypeVar, Protocol, Any, runtime_checkable

from typing_extensions import Self

from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('IComparableSchema', 'ComparableSchema')

_P = TypeVar('_P', covariant=True)
_T = TypeVar('_T')


@runtime_checkable
class IComparableSchema(Protocol[_P]):
    def le(self, limit: Any, message: ErrorMessage = locale["le"]) -> _P: ...

    def ge(self, limit: Any, message: ErrorMessage = locale["ge"]) -> _P: ...

    def lt(self, limit: Any, message: ErrorMessage = locale["lt"]) -> _P: ...

    def gt(self, limit: Any, message: ErrorMessage = locale["gt"]) -> _P: ...


class ComparableSchema(Schema[_T]):

    def le(self, limit: Any, message: ErrorMessage = locale["le"]) -> Self:
        def _(x: Any) -> None:
            if x > limit:
                raise ValidationError(Constraint("le", message, limit), invalid_value=x)

        return self.test(_)

    def ge(self, limit: Any, message: ErrorMessage = locale["ge"]) -> Self:
        def _(x: Any) -> None:
            if x < limit:
                raise ValidationError(Constraint("ge", message, limit), invalid_value=x)

        return self.test(_)

    def lt(self, limit: Any, message: ErrorMessage = locale["lt"]) -> Self:
        def _(x: Any) -> None:
            if x >= limit:
                raise ValidationError(Constraint("lt", message, limit), invalid_value=x)

        return self.test(_)

    def gt(self, limit: Any, message: ErrorMessage = locale["gt"]) -> Self:
        def _(x: Any) -> None:
            if x <= limit:
                raise ValidationError(Constraint("gt", message, limit), invalid_value=x)

        return self.test(_)
