from typing import TypeVar, Protocol, Any

from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('IComparable', 'ComparableSchema')

_P = TypeVar('_P', covariant=True)
_S = TypeVar('_S')


class IComparable(Protocol[_P]):
    def le(self, limit: Any, message: ErrorMessage = locale["le"]) -> _P: ...

    def ge(self, limit: Any, message: ErrorMessage = locale["ge"]) -> _P: ...

    def lt(self, limit: Any, message: ErrorMessage = locale["lt"]) -> _P: ...

    def gt(self, limit: Any, message: ErrorMessage = locale["gt"]) -> _P: ...


class ComparableSchema(Schema[_S]):

    def le(self, limit: Any, message: ErrorMessage = locale["le"]) -> _S:
        def _(x: Any) -> None:
            if x > limit:
                raise ValidationError(Constraint("le", limit, message))

        return self.test(_)

    def ge(self, limit: Any, message: ErrorMessage = locale["ge"]) -> _S:
        def _(x: Any) -> None:
            if x < limit:
                raise ValidationError(Constraint("ge", limit, message))

        return self.test(_)

    def lt(self, limit: Any, message: ErrorMessage = locale["lt"]) -> _S:
        def _(x: Any) -> None:
            if x >= limit:
                raise ValidationError(Constraint("lt", limit, message))

        return self.test(_)

    def gt(self, limit: Any, message: ErrorMessage = locale["gt"]) -> _S:
        def _(x: Any) -> None:
            if x <= limit:
                raise ValidationError(Constraint("gt", limit, message))

        return self.test(_)
