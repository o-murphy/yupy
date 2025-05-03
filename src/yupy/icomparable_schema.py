from typing import Protocol, Any, runtime_checkable

from typing_extensions import Self

from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('IComparableSchema', 'ComparableSchema')


@runtime_checkable
class IComparableSchema(Protocol):
    def le(self, limit: Any, message: ErrorMessage = locale["le"]) -> Self: ...

    def ge(self, limit: Any, message: ErrorMessage = locale["ge"]) -> Self: ...

    def lt(self, limit: Any, message: ErrorMessage = locale["lt"]) -> Self: ...

    def gt(self, limit: Any, message: ErrorMessage = locale["gt"]) -> Self: ...


class ComparableSchema(Schema):

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
